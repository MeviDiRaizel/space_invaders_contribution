import random
import os
import sys
import requests
from typing import List

def get_contributions(username: str) -> List[dict]:
    token = os.getenv('GH_TOKEN')
    if not token:
        raise EnvironmentError("GitHub token not found. Please set the GH_TOKEN environment variable.")
    
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': query, 'variables': {'username': username}},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            raise Exception(f"GitHub API Error: {data['errors']}")
        
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch GitHub data: {str(e)}")

def create_space_invader_svg(contributions, output_file: str):
    svg_template = f'''<svg width="900" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Retro CRT filter -->
        <filter id="crt">
            <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" />
            <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0" />
            <feComponentTransfer>
                <feFuncR type="discrete" tableValues="0 1" />
                <feFuncG type="discrete" tableValues="0 1" />
                <feFuncB type="discrete" tableValues="0 1" />
            </feComponentTransfer>
        </filter>
        
        <!-- Explosion effect -->
        <filter id="explosion">
            <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" result="turbulence"/>
            <feDisplacementMap in="SourceGraphic" in2="turbulence" scale="10" xChannelSelector="R" yChannelSelector="G"/>
            <feGaussianBlur stdDeviation="2" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <style>
            /* Retro game styling */
            @keyframes invader-move {{
                0%, 100% {{ transform: translateX(0); }}
                50% {{ transform: translateX(10px); }}
            }}
            
            @keyframes laser-beam {{
                0% {{ transform: translateY(180px); opacity: 1; }}
                100% {{ transform: translateY(-300px); opacity: 0; }}
            }}
            
            @keyframes explosion {{
                0% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(2); opacity: 0.5; }}
                100% {{ transform: scale(3); opacity: 0; }}
            }}
            
            .spaceship {{
                animation: invader-move 1s infinite;
            }}
            
            .laser {{
                stroke-dasharray: 5,5;
                animation: laser-beam 0.8s linear forwards;
            }}
            
            .contribution {{
                transition: all 0.3s;
            }}
            
            .explosion {{
                animation: explosion 0.5s ease-out forwards;
                filter: url(#explosion);
            }}
            
            /* CRT overlay effect */
            .crt-overlay {{
                filter: url(#crt);
                opacity: 0.1;
                pointer-events: none;
            }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="100%" height="100%" fill="#000"/>
    
    <!-- Stars -->
    {"".join(f'<circle cx="{random.randint(0, 900)}" cy="{random.randint(0, 300)}" r="{random.uniform(0.5, 1.5)}" fill="#fff" opacity="{random.uniform(0.3, 0.8)}"/>' 
             for _ in range(100))}
    
    <!-- Contribution Grid -->
    <g transform="translate(50,20)">
    {''.join(
        f'<g class="contribution" id="c-{week_idx}-{day_idx}">'
        f'<rect x="{week_idx * 15}" y="{day_idx * 15}" width="12" height="12" rx="2" fill="{get_color(day["contributionCount"])}">'
        f'<animate attributeName="fill" values="{get_color(day["contributionCount"])};#ff0000;{get_color(day["contributionCount"])}" dur="0.5s" begin="indefinite" fill="freeze" id="hit-{week_idx}-{day_idx}"/>'
        f'</rect>'
        f'<animateTransform attributeName="transform" type="scale" additive="sum" values="1;1.5;1" dur="0.5s" begin="hit-{week_idx}-{day_idx}.begin" fill="freeze"/>'
        f'</g>'
        for week_idx, week in enumerate(contributions)
        for day_idx, day in enumerate(week["contributionDays"])
        if day["contributionCount"] > 0
    )}
    </g>
    
    <!-- Player Spaceship -->
    <g class="spaceship" transform="translate(400,250)">
        <rect x="-15" y="-10" width="30" height="20" fill="#00ff00" rx="5"/>
        <path d="M -10 0 L 0 -15 L 10 0" fill="#ff0000"/>
        <animateMotion path="M 0 0 L -200 0 L 200 0 L 0 0" dur="8s" repeatCount="indefinite"/>
    </g>
    
    <!-- Laser Beams -->
    {''.join(
        f'<line class="laser" x1="{400 + random.randint(-10,10)}" y1="250" x2="{50 + week_idx * 15 + 6}" y2="{20 + day_idx * 15 + 6}" '
        f'stroke="#00ff00" stroke-width="2" opacity="0">'
        f'<animate id="laser-{week_idx}-{day_idx}" attributeName="opacity" values="0;1;0" dur="0.8s" begin="{random.uniform(0, 5)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="stroke-width" values="2;4;2" dur="0.2s" repeatCount="indefinite"/>'
        f'<animate begin="laser-{week_idx}-{day_idx}.begin" dur="0.001s" attributeName="x1" to="{400}" fill="freeze"/>'
        f'<animate begin="laser-{week_idx}-{day_idx}.begin+0.4s" dur="0.001s" target="hit-{week_idx}-{day_idx}" attributeName="begin" from="indefinite" to="laser-{week_idx}-{day_idx}.begin+0.4s"/>'
        f'</line>'
        for week_idx, week in enumerate(contributions)
        for day_idx, day in enumerate(week["contributionDays"])
        if day["contributionCount"] > 0
    )}
    
    <!-- CRT Overlay -->
    <rect width="100%" height="100%" fill="url(#crt-overlay)" class="crt-overlay"/>
    
    <!-- Sound Effects Visualization -->
    <g opacity="0.5">
        {"".join(f'<rect x="{random.randint(0, 900)}" y="{random.randint(0, 300)}" width="2" height="10" fill="#0f0" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;0" dur="0.1s" begin="laser-{random.randint(0,len(contributions))}-{random.randint(0,6)}.begin"/>'
                 '</rect>' 
                 for _ in range(20))}
    </g>
</svg>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_template)

def get_color(count: int) -> str:
    colors = {
        0: '#161b22',
        1: '#0e4429',
        3: '#006d32',
        6: '#26a641',
        9: '#39d353'
    }
    return next((v for k, v in colors.items() if count >= k), '#39d353')

if __name__ == "__main__":
    try:
        username = sys.argv[1] if len(sys.argv) > 1 else "MeviDiRaizel"
        print(f"Fetching contributions for user: {username}")
        
        data = get_contributions(username)
        
        if 'data' in data and 'user' in data['data']:
            weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
            output_path = os.path.join(os.getcwd(), 'contribution_space_invader.svg')
            create_space_invader_svg(weeks, output_path)
            print(f"Successfully generated SVG at: {output_path}")
        else:
            raise Exception("Invalid response format from GitHub API")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
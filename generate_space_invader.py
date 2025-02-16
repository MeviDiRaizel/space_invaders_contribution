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

def create_space_invader_svg(weeks, output_file: str):
    svg_template = f'''<svg width="900" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="explosion">
            <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
            <feColorMatrix in="blur" type="matrix"
                values="1 0 0 0 0  
                        0 1 0 0 0  
                        0 0 1 0 0  
                        0 0 0 18 -7"/>
        </filter>
        
        <style>
            @keyframes ship-move {{
                0% {{ transform: translateX(-200px); }}
                50% {{ transform: translateX(200px); }}
                100% {{ transform: translateX(-200px); }}
            }}
            
            @keyframes laser-shot {{
                0% {{ opacity: 1; transform: translateY(0); }}
                100% {{ opacity: 0; transform: translateY(-250px); }}
            }}
            
            @keyframes explode {{
                0% {{ transform: scale(1); opacity: 1; }}
                100% {{ transform: scale(2); opacity: 0; }}
            }}
            
            .spaceship {{
                animation: ship-move 4s linear infinite;
            }}
            
            .laser {{
                animation: laser-shot 0.8s linear infinite;
            }}
            
            .explosion {{
                animation: explode 0.3s ease-out forwards;
            }}
        </style>
    </defs>
    
    <rect width="100%" height="100%" fill="#0d1117"/>
    
    <!-- Contribution Grid -->
    <g transform="translate(50,20)">
    {''.join(
        f'<g class="contribution" id="c-{week_idx}-{day_idx}">'
        f'<rect x="{week_idx * 15}" y="{day_idx * 15}" width="12" height="12" rx="2" '
        f'fill="{get_color(day["contributionCount"])}">'
        f'<animate attributeName="opacity" from="1" to="0" dur="0.3s" '
        f'begin="laser-{week_idx}-{day_idx}.end" fill="freeze"/>'
        f'</rect>'
        f'<circle class="explosion" cx="{week_idx * 15 + 6}" cy="{day_idx * 15 + 6}" r="6" '
        f'fill="#ff4500" opacity="0" filter="url(#explosion)">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" '
        f'begin="laser-{week_idx}-{day_idx}.end" fill="freeze"/>'
        f'</circle>'
        f'</g>'
        for week_idx, week in enumerate(weeks)
        for day_idx, day in enumerate(week["contributionDays"])
        if day["contributionCount"] > 0
    )}
    </g>
    
    <!-- Animated Space Invader Ship -->
    <g class="spaceship" transform="translate(450,270)">
        <!-- Ship body -->
        <rect x="-20" y="-10" width="40" height="20" fill="#2ebd2e" rx="5"/>
        <!-- Ship top -->
        <path d="M -15 0 Q 0 -20 15 0" fill="#1a7a1a"/>
        <!-- Cannon -->
        <rect x="-5" y="-15" width="10" height="5" fill="#ff0000"/>
        
        <!-- Shooting Lasers -->
        {''.join(
            f'<line class="laser" x1="0" y1="-10" x2="{50 + week_idx * 15 + 6 - 450}" y2="{20 + day_idx * 15 + 6 - 270}" '
            f'stroke="#00ff00" stroke-width="2" stroke-linecap="round" opacity="0">'
            f'<animate id="laser-{week_idx}-{day_idx}" attributeName="opacity" '
            f'values="0;1;0" dur="1s" begin="{random.uniform(0, 2)}s" repeatCount="indefinite"/>'
            f'</line>'
            for week_idx, week in enumerate(weeks)
            for day_idx, day in enumerate(week["contributionDays"])
            if day["contributionCount"] > 0
        )}
    </g>
</svg>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_template)

def get_color(count: int) -> str:
    if count == 0:
        return '#161b22'
    elif count <= 3:
        return '#0e4429'
    elif count <= 6:
        return '#006d32'
    elif count <= 9:
        return '#26a641'
    else:
        return '#39d353'

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
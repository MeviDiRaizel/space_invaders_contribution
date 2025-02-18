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
    def laser_lines():
        return '''
        <line class="laser" x1="0" y1="0" x2="0" y2="0"
            stroke="#ff0000" stroke-width="2" stroke-linecap="round">
            <animate attributeName="y2" values="0;-220" dur="0.3s" 
                begin="0s;laser-opacity.end+0.7s" fill="freeze" id="laser-move"/>
            <animate attributeName="opacity" values="1;1;0" dur="0.3s"
                begin="0s;laser-opacity.end+0.7s" id="laser-opacity"/>
        </line>'''

    svg_template = f'''<svg width="900" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="explosion">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2"/>
            <feColorMatrix type="matrix" values="1 0 0 0 1  0 1 0 0 0.5  0 0 1 0 0  0 0 0 1 0"/>
        </filter>
        
        <style>
            @keyframes ship-move {{
                0% {{ transform: translateX(50px); }}
                100% {{ transform: translateX(750px); }}
            }}
            .spaceship {{
                animation: ship-move 6s linear infinite alternate;
            }}
            .contribution-box {{
                transition: opacity 0.3s;
            }}
            @keyframes explode {{
                0% {{ transform: scale(1); opacity: 1; }}
                100% {{ transform: scale(2); opacity: 0; }}
            }}
            .explosion {{
                animation: explode 0.5s ease-out forwards;
            }}
        </style>
    </defs>
    
    <rect width="100%" height="100%" fill="#0d1117"/>
    
    <!-- Stars background -->
    {"".join(f'<circle cx="{random.randint(0, 900)}" cy="{random.randint(0, 300)}" r="1" fill="white" opacity="{random.uniform(0.3, 1)}"><animate attributeName="opacity" values="{random.uniform(0.3, 0.7)};1;{random.uniform(0.3, 0.7)}" dur="{random.uniform(1, 3)}s" repeatCount="indefinite"/></circle>' for _ in range(50))}
    
    <!-- Contribution Grid -->
    <g transform="translate(50,20)" id="contribution-grid">
    {''.join(
        f'<g class="contribution-group" id="contrib-{week_idx}-{day_idx}">'
        f'<rect class="contribution-box" x="{week_idx * 15}" y="{day_idx * 15}" '
        f'width="12" height="12" rx="2" fill="{get_color(day["contributionCount"])}"/>'
        f'</g>'
        for week_idx, week in enumerate(weeks)
        for day_idx, day in enumerate(week["contributionDays"])
        if day["contributionCount"] > 0
    )}
    </g>
    
    <!-- Space Invader Ship -->
    <g class="spaceship">
        <g transform="translate(0,280)">
            <!-- Ship body (facing upward) -->
            <path d="M-15,10 L0,-20 L15,10 L0,0 Z" fill="#61dafb"/>
            <!-- Ship cannon -->
            <rect x="-3" y="-15" width="6" height="8" fill="#ff0000"/>
            
            <!-- Auto-firing laser -->
            {laser_lines()}
        </g>
    </g>

    <script><![CDATA[
        function createExplosion(x, y) {{
            const explosion = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            explosion.setAttribute("cx", x + 6);
            explosion.setAttribute("cy", y + 6);
            explosion.setAttribute("r", "8");
            explosion.setAttribute("fill", "#ff4500");
            explosion.setAttribute("filter", "url(#explosion)");
            explosion.classList.add("explosion");
            return explosion;
        }}

        const laser = document.querySelector('.laser');
        const grid = document.getElementById('contribution-grid');
        
        laser.addEventListener('beginEvent', () => {{
            const checkCollision = setInterval(() => {{
                const boxes = document.querySelectorAll('.contribution-box');
                const laserBox = laser.getBoundingClientRect();
                
                for (const box of boxes) {{
                    const boxRect = box.getBoundingClientRect();
                    if (laserBox.x >= boxRect.x && 
                        laserBox.x <= boxRect.x + boxRect.width &&
                        laserBox.y <= boxRect.y + boxRect.height) {{
                            
                        const explosion = createExplosion(
                            parseInt(box.getAttribute('x')),
                            parseInt(box.getAttribute('y'))
                        );
                        
                        box.parentElement.appendChild(explosion);
                        box.style.opacity = 0;
                        setTimeout(() => {{
                            box.remove();
                            explosion.remove();
                        }}, 500);
                        
                        clearInterval(checkCollision);
                        break;
                    }}
                }}
            }}, 50);

            setTimeout(() => clearInterval(checkCollision), 300);
        }});
    ]]></script>
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
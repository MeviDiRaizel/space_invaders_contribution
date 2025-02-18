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
        laser_svg = ""
        for week_idx, week in enumerate(weeks):
            for day_idx, day in enumerate(week["contributionDays"]):
                if day["contributionCount"] > 0:
                    laser_svg += (
                        f"""<line class="laser" x1="0" y1="0" x2="0" y2="-220"
                        stroke="#ff0000" stroke-width="2" opacity="0">
                        <animate id="laser-{week_idx}-{day_idx}"
                            attributeName="opacity"
                            values="0;1;0"
                            dur="0.3s"
                            begin="{week_idx + day_idx}s"
                            repeatCount="1"/>
                        </line>"""
                    )
        return laser_svg

    svg_template = f'''<svg width="900" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="explosion">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2"/>
            <feColorMatrix type="matrix" values="
                1 0 0 0 1
                0 1 0 0 0.5
                0 0 1 0 0
                0 0 0 1 0"/>
        </filter>
        
        <style>
            @keyframes ship-move {{
                0% {{ transform: translateX(50px); }}
                100% {{ transform: translateX(750px); }}
            }}
            @keyframes laser-shot {{
                from {{ transform: scaleY(0); }}
                to {{ transform: scaleY(1); }}
            }}
            .spaceship {{
                animation: ship-move 6s linear infinite alternate;
            }}
            .contribution-box {{
                transition: all 0.3s ease-out;
            }}
            .explosion {{
                transform-origin: center;
                animation: explode 0.5s ease-out forwards;
            }}
            @keyframes explode {{
                0% {{ transform: scale(0); opacity: 1; }}
                100% {{ transform: scale(2); opacity: 0; }}
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
        f'width="12" height="12" rx="2" fill="{get_color(day["contributionCount"])}">'
        f'<animate attributeName="opacity" from="1" to="0" dur="0.3s" begin="laser-{week_idx}-{day_idx}.begin" fill="freeze"/>'
        f'</rect>'
        f'<circle class="explosion" cx="{week_idx * 15 + 6}" cy="{day_idx * 15 + 6}" '
        f'r="8" fill="#ff4500" opacity="0" filter="url(#explosion)">'
        f'<animate attributeName="opacity" values="0;1;0" dur="0.5s" begin="laser-{week_idx}-{day_idx}.begin"/>'
        f'</circle></g>'
        for week_idx, week in enumerate(weeks)
        for day_idx, day in enumerate(week["contributionDays"])
        if day["contributionCount"] > 0
    )}
    </g>
    
    <!-- Space Invader Ship -->
    <g class="spaceship" transform="translate(0,270)">
        <path d="M-20,0 L0,-20 L20,0 L10,10 L-10,10 Z" fill="#61dafb"/>
        <circle cx="0" cy="-5" r="3" fill="#ff0000"/>
        
        <!-- Auto-firing lasers -->
        {laser_lines()}
    </g>
    
    <script>
        function resetAnimation() {{
            var grid = document.getElementById('contribution-grid');
            while (grid.firstChild) {{
                grid.removeChild(grid.firstChild);
            }}
            
            // Reload the SVG to restart the animation
            var svgElement = document.querySelector('svg');
            var newSvgElement = svgElement.cloneNode(true);
            svgElement.parentNode.replaceChild(newSvgElement, svgElement);
        }}
        
        // Check if all contribution boxes are destroyed
        function checkContributions() {{
            var contributions = document.querySelectorAll('.contribution-box');
            if (contributions.length === 0) {{
                resetAnimation();
            }}
        }}
        
        // Call checkContributions periodically
        setInterval(checkContributions, 5000);
    </script>
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
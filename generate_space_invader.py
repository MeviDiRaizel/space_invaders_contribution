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
    svg_template = f'''<svg width="900" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#0d1117"/>
    
    <!-- Stars -->
    {"".join(f'<circle cx="{random.randint(0, 900)}" cy="{random.randint(0, 200)}" r="1" fill="white"><animate attributeName="opacity" values="0.2;1;0.2" dur="3s" repeatCount="indefinite"/></circle>' for _ in range(50))}
    
    <!-- Contributions -->
    {''.join(
        f'<rect x="{x}" y="{y}" width="10" height="10" fill="{color}">'
        f'<animate attributeName="opacity" values="1;0" dur="0.5s" begin="spaceship.mouseover" fill="freeze"/>'
        f'</rect>'
        for week in contributions
        for day in week['contributionDays']
        for x, y, color in [(
            50 + (15 * ((week['contributionDays'].index(day) + len(contributions) * 7) % 53)),
            20 + (15 * ((week['contributionDays'].index(day) + len(contributions) * 7) // 53)),
            '#ff0000' if day['contributionCount'] > 10 else '#ffff00' if day['contributionCount'] > 5 else '#00ff00'
        )] if day['contributionCount'] > 0
    )}
    
    <!-- Spaceship -->
    <g id="spaceship">
        <animateTransform attributeName="transform" type="translate" values="0,0; 800,0; 0,0" dur="8s" repeatCount="indefinite"/>
        <polygon points="10,180 30,160 50,180" fill="#61dafb"/>
        <polygon points="15,180 25,185 35,180" fill="white"/>
        <circle cx="30" cy="170" r="3" fill="red"/>
        <line x1="30" y1="160" x2="30" y2="20" stroke="red" stroke-width="2">
            <animate attributeName="opacity" values="0;1;0" dur="0.5s" repeatCount="indefinite"/>
        </line>
    </g>
</svg>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_template)

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
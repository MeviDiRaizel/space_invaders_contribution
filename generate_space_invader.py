import random
import os
import sys
import datetime
import requests
import json
from typing import List
import svgwrite
from svgwrite import animate

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
    dwg = svgwrite.Drawing(output_file, profile='tiny', size=(900, 200))
    
    # Add background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0d1117'))
    
    # Create enhanced spaceship
    spaceship = dwg.g(id='spaceship')
    # Main body
    spaceship.add(dwg.polygon(points=[(10, 180), (30, 160), (50, 180)], fill='#61dafb'))
    # Wings
    spaceship.add(dwg.polygon(points=[(15, 180), (25, 185), (35, 180)], fill='#ffffff'))
    # Cockpit
    spaceship.add(dwg.circle(center=(30, 170), r=3, fill='#ff0000'))
    
    # Add laser beam
    laser = dwg.g(id='laser')
    laser.add(dwg.line(start=(30, 160), end=(30, 20), stroke='#ff0000', stroke_width=2))
    laser_animate = dwg.animate(
        attributeName='opacity',
        values='0;1;0',  # Changed from list to string
        dur='0.5s',
        repeatCount='indefinite'
    )
    laser.add(laser_animate)
    dwg.add(laser)
    
    # Process contribution data
    x, y = 50, 20
    for week in contributions:
        for day in week['contributionDays']:
            count = day['contributionCount']
            if count > 0:
                color = '#ff0000' if count > 10 else '#ffff00' if count > 5 else '#00ff00'
                
                target = dwg.g(id=f'target-{x}-{y}')
                target.add(dwg.rect(insert=(x, y), size=(10, 10), fill=color))
                
                explosion = dwg.g(id=f'explosion-{x}-{y}', opacity=0)
                explosion.add(dwg.circle(center=(x+5, y+5), r=8, fill='#ff4500'))
                explosion.add(dwg.animate(
                    attributeName='opacity',
                    values='0;1;0',  # Changed from list to string
                    dur='0.5s',
                    begin='indefinite'
                ))
                dwg.add(target)
                dwg.add(explosion)
            
            x += 15
            if x > 850:
                x = 50
                y += 15
    
    # Add spaceship animation
    spaceship_animate = dwg.animate(
        attributeName='transform',
        values='translate(0,0);translate(800,0);translate(0,0)',  # Changed from list to string
        dur='8s',
        repeatCount='indefinite'
    )
    spaceship.add(spaceship_animate)
    dwg.add(spaceship)
    
    # Add stars
    for _ in range(50):
        x = random.randint(0, 900)
        y = random.randint(0, 200)
        star = dwg.circle(center=(x, y), r=1, fill='#ffffff')
        star_animate = dwg.animate(
            attributeName='opacity',
            values='0.2;1;0.2',  # Changed from list to string
            dur='2s',
            repeatCount='indefinite'
        )
        star.add(star_animate)
        dwg.add(star)
    
    # Save the SVG file
    dwg.save()

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
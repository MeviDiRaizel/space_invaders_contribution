import os
import sys
import datetime
import requests
import json
from typing import List
import svgwrite
from svgwrite import animate

def get_contributions(username: str) -> List[dict]:
    # GitHub GraphQL query remains the same
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
    
    headers = {"Authorization": f"Bearer {os.getenv('GH_TOKEN')}"}
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': {'username': username}},
        headers=headers
    )
    
    return response.json()

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
    laser_animate = dwg.animate(attributeName='opacity', values='0;1;0', dur='0.5s', repeatCount='indefinite')
    laser.add(laser_animate)
    dwg.add(laser)
    
    # Add contributions as targets with different colors based on count
    x, y = 50, 20
    for contrib in contributions:
        if contrib['contributionCount'] > 0:
            # Color gradient based on contribution count
            if contrib['contributionCount'] > 10:
                color = '#ff0000'  # Red for high contributions
            elif contrib['contributionCount'] > 5:
                color = '#ffff00'  # Yellow for medium contributions
            else:
                color = '#00ff00'  # Green for low contributions
                
            target = dwg.g(id=f'target-{x}-{y}')
            target.add(dwg.rect(insert=(x, y), size=(10, 10), fill=color))
            
            # Add explosion animation
            explosion = dwg.g(id=f'explosion-{x}-{y}', opacity=0)
            explosion.add(dwg.circle(center=(x+5, y+5), r=8, fill='#ff4500'))
            explosion.add(dwg.animate(attributeName='opacity', values='0;1;0', dur='0.5s', begin='indefinite'))
            dwg.add(explosion)
            
            dwg.add(target)
        x += 15
        if x > 850:
            x = 50
            y += 15
    
    # Spaceship movement animation
    spaceship_animate = dwg.animate()
    spaceship_animate['attributeName'] = 'transform'
    spaceship_animate['values'] = 'translate(0,0); translate(800,0); translate(0,0)'
    spaceship_animate['dur'] = '8s'
    spaceship_animate['repeatCount'] = 'indefinite'
    spaceship.add(spaceship_animate)
    
    # Add spaceship to drawing
    dwg.add(spaceship)
    
    # Add some stars in background
    for _ in range(50):
        x = random.randint(0, 900)
        y = random.randint(0, 200)
        star = dwg.circle(center=(x, y), r=1, fill='#ffffff')
        star_animate = dwg.animate(attributeName='opacity', values='0.2;1;0.2', dur='2s', repeatCount='indefinite')
        star.add(star_animate)
        dwg.add(star)
    
    dwg.save()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "MeviDiRaizel"
    data = get_contributions(username)
    create_space_invader_svg(
        data['data']['user']['contributionsCollection']['contributionCalendar']['weeks'],
        'contribution_space_invader.svg'
    )
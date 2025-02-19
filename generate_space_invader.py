import requests
import datetime
import math
import random

def get_github_contributions(username):
    now = datetime.datetime.now()
    last_year = now - datetime.timedelta(days=365)
    query = '''
    query {
        user(login: "%s") {
            contributionsCollection(from: "%s", to: "%s") {
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
    ''' % (username, last_year.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

    headers = {
        'Authorization': f'Bearer {github_token}' if 'github_token' in globals() else None
    }
    
    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    data = response.json()
    return data['data']['user']['contributionsCollection']['contributionCalendar']

def generate_space_invader_svg(username):
    contributions = get_github_contributions(username)
    weeks = contributions['weeks']
    
    # SVG dimensions and settings
    cell_size = 10
    cell_padding = 2
    week_count = len(weeks)
    width = (week_count * (cell_size + cell_padding))
    height = (7 * (cell_size + cell_padding)) + 100  # Extra space for spaceship
    
    # Create SVG header with animation definitions
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" 
         xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Explosion animation -->
        <radialGradient id="explosion" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0%" stop-color="#ff8c00"/>
            <stop offset="100%" stop-color="#ff4500"/>
        </radialGradient>
        
        <!-- Spaceship movement animation -->
        <animate id="shipMove" 
                attributeName="x"
                from="0"
                to="{width - 30}"
                dur="4s"
                repeatCount="indefinite"
                begin="0s"
                fill="freeze"
                calcMode="linear"
                keyTimes="0;0.4;0.6;1"
                values="0;{width - 30};{width - 30};0"/>
    </defs>
    
    <!-- Background -->
    <rect width="100%" height="100%" fill="#0d1117"/>
    
    <!-- Contribution grid -->
    '''
    
    # Generate contribution boxes
    boxes = []
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week['contributionDays']):
            count = day['contributionCount']
            if count > 0:
                x = week_index * (cell_size + cell_padding)
                y = day_index * (cell_size + cell_padding)
                color = '#39d353' if count > 0 else '#161b22'
                box_id = f'box_{week_index}_{day_index}'
                
                boxes.append(f'''
    <g id="{box_id}">
        <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" 
              fill="{color}" rx="2" ry="2">
            <animate id="explode_{box_id}" 
                     attributeName="opacity"
                     from="1" to="0"
                     dur="0.3s"
                     begin="indefinite"
                     fill="freeze"/>
        </rect>
    </g>''')
    
    svg += '\n'.join(boxes)
    
    # Add spaceship
    spaceship_y = height - 40
    svg += f'''
    <!-- Spaceship -->
    <g id="spaceship">
        <path d="M15 {spaceship_y} l-15 20 h30 l-15 -20" fill="#4a9eff">
            <animateMotion dur="4s" repeatCount="indefinite">
                <mpath href="#shipPath"/>
            </animateMotion>
        </path>
    </g>
    
    <!-- Spaceship path -->
    <path id="shipPath" d="M0 0 H{width - 30} H0" fill="none" visibility="hidden"/>
    
    <!-- Projectiles and explosions -->
    <script type="text/javascript"><![CDATA[
        function createProjectile(x, y) {
            const projectile = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            const svgRect = document.querySelector("svg").getBoundingClientRect();
            const adjustedX = (x - svgRect.left) * (width / svgRect.width);
            projectile.setAttribute("cx", adjustedX);
            projectile.setAttribute("cy", y);
            projectile.setAttribute("r", "3");
            projectile.setAttribute("fill", "#ff0");
            
            const anim = document.createElementNS("http://www.w3.org/2000/svg", "animate");
            anim.setAttribute("attributeName", "cy");
            anim.setAttribute("from", y);
            anim.setAttribute("to", "0");
            anim.setAttribute("dur", "1s");
            anim.setAttribute("fill", "freeze");
            
            projectile.appendChild(anim);
            document.querySelector("svg").appendChild(projectile);
            
            anim.beginElement();
            
            // Check for collisions with improved timing and accuracy
            const checkCollision = () => {
                const projectileY = parseFloat(projectile.getAttribute("cy"));
                const boxes = document.querySelectorAll('[id^="box_"]');
                
                boxes.forEach(box => {
                    const rect = box.querySelector('rect');
                    const boxX = parseFloat(rect.getAttribute('x'));
                    const boxY = parseFloat(rect.getAttribute('y'));
                    
                    if (Math.abs(boxX - adjustedX) < 8 && Math.abs(boxY - projectileY) < 8) {
                        const explodeAnim = document.querySelector(`#explode_${box.id}`);
                        if (explodeAnim && !explodeAnim.hasAttribute('begun')) {
                            explodeAnim.setAttribute('begun', 'true');
                            explodeAnim.beginElement();
                            createExplosion(boxX, boxY);
                            projectile.remove();
                        }
                    }
                });
                
                if (projectileY > 0 && projectile.parentNode) {
                    requestAnimationFrame(checkCollision);
                }
            };
            
            requestAnimationFrame(checkCollision);
        }
        
        function createExplosion(x, y) {
            const explosion = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            explosion.setAttribute("cx", x + 5);
            explosion.setAttribute("cy", y + 5);
            explosion.setAttribute("r", "0");
            explosion.setAttribute("fill", "url(#explosion)");
            
            const scaleAnim = document.createElementNS("http://www.w3.org/2000/svg", "animate");
            scaleAnim.setAttribute("attributeName", "r");
            scaleAnim.setAttribute("from", "0");
            scaleAnim.setAttribute("to", "10");
            scaleAnim.setAttribute("dur", "0.3s");
            scaleAnim.setAttribute("fill", "freeze");
            
            const fadeAnim = document.createElementNS("http://www.w3.org/2000/svg", "animate");
            fadeAnim.setAttribute("attributeName", "opacity");
            fadeAnim.setAttribute("from", "1");
            fadeAnim.setAttribute("to", "0");
            fadeAnim.setAttribute("dur", "0.3s");
            fadeAnim.setAttribute("fill", "freeze");
            
            explosion.appendChild(scaleAnim);
            explosion.appendChild(fadeAnim);
            document.querySelector("svg").appendChild(explosion);
            
            scaleAnim.beginElement();
            fadeAnim.beginElement();
            
            setTimeout(() => explosion.remove(), 300);
        }
        
        // Fire projectiles with corrected position tracking
        setInterval(() => {
            const ship = document.querySelector("#spaceship");
            const shipRect = ship.getBoundingClientRect();
            createProjectile(shipRect.x, spaceship_y);
        }, 1000);
    ]]></script>
    </svg>'''
    
    return svg

def main():
    # Replace with your GitHub username
    username = 'your_username'
    svg_content = generate_space_invader_svg(username)
    
    with open('contribution_space_invader.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)

if __name__ == '__main__':
    main()
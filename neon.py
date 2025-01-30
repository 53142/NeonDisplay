import adafruit_display_text.label
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time
import requests
from datetime import datetime

forecast = requests.get("https://api.open-meteo.com/v1/forecast?latitude=40.7143&longitude=-74.006&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&current=weather_code&forecast_days=1").json()
# print(forecast)
weatherCode = forecast["current"]["weather_code"]
days = [day.split("-")[2]+":" for day in forecast['daily']['time']]
maxTemps = [str(high).split(".")[0] for high in forecast['daily']['temperature_2m_max']]
minTemps = [str(low).split(".")[0] for low in forecast['daily']['temperature_2m_min']]

counter = 0
prevtext = ""
last_fetch_time = 0  # Track last fetch time

def get_github_top_repo():
    global last_fetch_time, prevtext

    # Fetch new data only every 10 minutes
    if time.time() - last_fetch_time < 600:
        return prevtext  # Use cached value

    last_fetch_time = time.time()  # Update fetch time

    today = datetime.utcnow().strftime("%Y-%m-%d")  # Get today's date in UTC
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent request blocking

    urls = [
        f"https://api.github.com/search/repositories?q=created:{today}&sort=stars&order=desc"
    ]

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                repos = response.json().get("items", [])
                if repos:
                    prevtext = f"🔥 Trending Today: {repos[0]['full_name']} ⭐ {repos[0]['stargazers_count']}"
                    return prevtext
            elif response.status_code == 403:
                prevtext = "⚠️ GitHub API Rate Limit Reached"
                return prevtext
        except requests.RequestException as e:
            prevtext = f"⚠️ GitHub Error: {str(e)}"

    return prevtext  # Use previous value if all requests fail

prevtext = get_github_top_repo()

def get_weather_condition(code):
    if code in [0]:
        return "sunny"
    elif code in [1, 2, 3]:
        return "cloudy"
    elif code in range(51, 57) or code in range(61, 68) or code in range(80, 83):
        return "rainy"
    else:
        return "unknown"

weather = get_weather_condition(weatherCode)

weatherText = ""
for i in range(len(maxTemps)):
    weatherText += "L" + str(minTemps[i]) + " H" + str(maxTemps[i])

# Release any previous display
displayio.release_displays()

# Setup the RGB matrix
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)

# Associate RGB matrix with display
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

# Create the temperature text label
line1 = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0xff0000,
    text=weatherText)
line1.x = 0
line1.y = 4

# Time/date label
line2 = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0x00ff00,
    text="00/00 00:00:00")
line2.x = 0
line2.y = 14

# Scroll label
line3 = adafruit_display_text.label.Label(
    terminalio.FONT, color=0xFFFFFF, text="test")
line3.x = 0
line3.y = 24

if weather == "sunny":

    # Create a bitmap for the sun icon
    sun_bitmap = displayio.Bitmap(10, 10, 2)  # 10x10 pixel bitmap, 2 colors
    sun_palette = displayio.Palette(2)
    sun_palette[0] = 0x000000  # Black (transparent)
    sun_palette[1] = 0xFFFF00  # Yellow
    
    sun_pattern = [
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]


    for y, row in enumerate(sun_pattern):
        for x, value in enumerate(row):
            sun_bitmap[x, y] = value
    
    tilegrid = displayio.TileGrid(sun_bitmap, pixel_shader=sun_palette)
    tilegrid.x = 50
    tilegrid.y = 5

elif weather == "rainy":
    rain_bitmap = displayio.Bitmap(10, 10, 2)  # 10x10 pixel bitmap, 2 colors
    rain_palette = displayio.Palette(2)
    rain_palette[0] = 0x000000  # Black (transparent)
    rain_palette[1] = 0x0000FF  # Blue
    
    raindrop_pattern = [
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    ]



    for y, row in enumerate(raindrop_pattern):
        for x, value in enumerate(row):
            rain_bitmap[x, y] = value
    
    tilegrid = displayio.TileGrid(rain_bitmap, pixel_shader=rain_palette)
    tilegrid.x = 52
    tilegrid.y = 5
else:
    cloud_bitmap = displayio.Bitmap(10, 10, 2)  # 10x10 pixel bitmap, 2 colors
    cloud_palette = displayio.Palette(2)
    cloud_palette[0] = 0x000000  # Black (transparent)
    cloud_palette[1] = 0xFFFFFF  # White
    
    cloud_pattern = [
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    ]



    for y, row in enumerate(cloud_pattern):
        for x, value in enumerate(row):
            cloud_bitmap[x, y] = value
    
    tilegrid = displayio.TileGrid(cloud_bitmap, pixel_shader=cloud_palette)
    tilegrid.x = 50
    tilegrid.y = 0


# Group all display elements
g = displayio.Group()
g.append(line1)
g.append(line2)
g.append(line3)
g.append(tilegrid)
display.root_group = g

def scroll(line):
    line.x = line.x - 1
    line_width = line.bounding_box[2]
    if line.x < -line_width:
        line.x = display.width

# Function to update time
def update_time():
    current_time = time.localtime()
    line2.text = f"{current_time.tm_mon:02d}/{current_time.tm_mday:02d} {current_time.tm_hour:02d}{current_time.tm_min:02d}"
    
    line3.text = f"{get_github_top_repo()} Weather: {weather.capitalize()} | High: {maxTemps[0]}°F, Low: {minTemps[0]}°F"

# Main loop
while True:
    scroll(line3)  # Scroll second line
    update_time()  # Update time display
    display.refresh(minimum_frames_per_second=0)
    time.sleep(0.02)

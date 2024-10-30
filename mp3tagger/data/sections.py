import json
import os

# Load sections from JSON
def load_sections():
    try:
        config_file = os.path.join(os.path.dirname(__file__), "sections_config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading sections config: {e}")
    
    # Return default sections if loading fails
    return [
        {
            "group_control": 0,  # NEUTRAL
            "label": "%_folderpath%",
            "order": 0,
            "scales": [
                ("ideas", 0),
                ("solo", 0),
                ("covers", 0),
                ("previous", 0),
                ("hold", 0),
                ("Boxify", 0),
                ("beats", 0),
            ],
        }
        
    ]

sections_data = load_sections()
sections_data.sort(key=lambda x: x.get("order", 0))
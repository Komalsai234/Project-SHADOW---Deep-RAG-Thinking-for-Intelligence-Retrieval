import subprocess
import sys

def run():
    try:
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/ui/streamlit_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
    except KeyboardInterrupt:
        print("Streamlit stopped.")

if __name__ == "__main__":
    run()
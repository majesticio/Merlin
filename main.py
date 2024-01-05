import multiprocessing
import subprocess
import os

def run_script(script_path, redirect_output=False):
    if redirect_output:
        with open(os.devnull, 'w') as devnull:
            subprocess.run(f"python {script_path}", shell=True, stdout=devnull, stderr=devnull)
    else:
        subprocess.run(f"python {script_path}", shell=True)

if __name__ == "__main__":
    background_scripts = ["transcriber.py", "responder.py", "speaker.py"]
    processes = []

    # Start background scripts in separate processes with redirected output
    for script in background_scripts:
        process = multiprocessing.Process(target=run_script, args=(script, True))
        process.start()
        processes.append(process)

    # Run recorder.py in the main thread for direct interaction
    run_script("recorder.py", redirect_output=False)

    # Wait for all background processes to complete
    for process in processes:
        process.join()

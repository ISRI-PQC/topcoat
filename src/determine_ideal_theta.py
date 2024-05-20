import shutil
import datetime
import re


from run_locally import main

SESSIONS_START = 2
SESSIONS_END = 15
ATTEMPTS = 10

if __name__ == "__main__":
    sign_pattern = re.compile(r"finished sign in (\d+\.\d+) seconds")
    now = datetime.datetime.now()

    sign_results = {}

    for sessions in range(SESSIONS_START, SESSIONS_END + 1):
        with open("src/topcoat/params.py", "r") as file:
            lines = file.readlines()

        parallel_line_index = next(
            (
                index
                for index, line in enumerate(lines)
                if line.startswith("PARALLEL_SESSIONS")
            ),
            None,
        )

        if parallel_line_index is None:
            raise Exception("PARALLEL_SESSIONS not found")

        lines[
            parallel_line_index
        ] = f"PARALLEL_SESSIONS = {sessions}  # How many commitments to do in parallel\n"

        with open("src/topcoat/params.py", "w") as file:
            file.writelines(lines)

        shutil.rmtree(f"logs/{now.strftime('%Y-%m-%d')}", ignore_errors=True)

        for attempts in range(1, ATTEMPTS + 1):
            print(f"Sessions: {sessions}, Attempts: {attempts}")
            try:
                main()
            except Exception as e:
                print(e)
                continue

        sign_times = []
        with open(f"logs/{now.strftime('%Y-%m-%d')}/Alice.log", "r") as file:
            for line in file:
                matches = sign_pattern.findall(line)
                if matches:
                    sign_times.extend([float(value) for value in matches])
        with open(f"logs/{now.strftime('%Y-%m-%d')}/Bob.log", "r") as file:
            for line in file:
                matches = sign_pattern.findall(line)
                if matches:
                    sign_times.extend([float(value) for value in matches])

        average = sum(sign_times) / len(sign_times)
        sign_results[sessions] = (average, sign_times)

    print(sign_results)

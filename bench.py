"""Benchmarks"""
import subprocess

opponents = {
    "bob": '"a=BOB;agents/TestAgents/bob/bobagent"',
    "jim": '"a=JIM;agents/TestAgents/jimmie/Agentjimmie"',
    "jon": '"a=JON;agents/TestAgents/joni/joniagent"',
}

if __name__ == "__main__":

    for i in range(5):
        for name, command in opponents.items():
            print(f"Playing {name}, game {i}")
            # p = subprocess.Popen(["python3", "Hex.py", f'"a=US;python3 ../AIandGames/beta-zero/protocol.py" {command}'],
            #                      cwd="/home/aaron/Programming/uni/AI/",
            #                      stdout=None,
            #                      stderr=subprocess.PIPE)

            args = ["python3", "Hex.py", '"a=US;python3 ../AIandGAMES/beta-zero/protocol.py"', command]
            p = subprocess.Popen(" ".join(args),
                                 cwd="/home/aaron/Programming/uni/AI/",
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)


            out, err = p.communicate()
            if out:
                print("Out:", out)
            if err:
                print("Err:", err)
            print("finnished")
            win = err.splitlines()[-2].split()[0]
            win = "w" if win == "True" else "l"
            subprocess.run(["mv", "bench.txt", f"benches/bench-{i}-{name}-{win}.csv"], check=True)

            print(f"Stored {name}, game {i}")

# python3 Hex.py -p "a=PNA;python3 ../'AI and Games'/beta-zero/protocol.py" "a=ANA;agents/TestAgents/bob/bobagent"

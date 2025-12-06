from src import preprocess
from src import modelBuilder as mb


def main():
    print("Hello from aurorabatteryoptimisation!")

    dfs = preprocess.preprocess_run()
    mb.run(dfs=dfs)


if __name__ == "__main__":
    main()

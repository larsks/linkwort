import argparse


def parse_args():
    p = argparse.ArgumentParser()
    return p.parse_args()


def main():
    args = parse_args()
    if hasattr(args, 'foo'):
        print('has foo')

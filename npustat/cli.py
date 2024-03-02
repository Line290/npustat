#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time

from blessed import Terminal

from .core import new_query
from npustat import __version__


def check_npu_smi():
    """ 检测命令 npu-smi info 是否能够正常工作 """
    result = os.popen("npu-smi info").read()
    if len(result.strip()) <= 0:
        sys.stderr.write(f"命令: npu-smi info 不存在，请检查是否正确安装了toolkit，并且正确配置了环境变量\n")
        exit(1)
    else:
        return True


def print_atlas_stat(json=False, debug=False, *args, **kwargs):
    """
    Display the Atlas query results into standard output.
    """
    try:
        atlas_stat = new_query(*args, **kwargs)
    except Exception as e:
        sys.stderr.write("获取 Atlas 设备信息报错。请在参数中添加上 \"--debug\" 获取报错的详情信息.")
        if debug:
            try:
                import traceback
                traceback.print_exc(file=sys.stderr)
            except Exception:
                raise e
        sys.exit(1)

    if json:
        atlas_stat.print_json(sys.stdout)
    else:
        atlas_stat.print_formatted(sys.stdout, **kwargs)


def loop_atlas_stat(interval=1.0, *args, **kwargs):
    term = Terminal()

    with term.fullscreen():
        while 1:
            try:
                query_start = time.time()

                # Move cursor to (0, 0) but do not restore original cursor loc
                print(term.move(0, 0), end="")
                print_atlas_stat(eol_char=term.clear_eol + os.linesep, *args, **kwargs)
                print(term.clear_eos, end="")

                query_duration = time.time() - query_start
                sleep_duration = interval - query_duration
                if sleep_duration > 0:
                    time.sleep(sleep_duration)
            except KeyboardInterrupt:
                return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", default=False,
                        help="将所有结果输出为JSON格式；")

    parser.add_argument("-i", "--interval", "--watch", nargs="?", type=float, default=0,
                        help="动态刷新模式；INTERVAL为刷新间隔，单位：秒；默认每2秒刷新一次；")

    parser.add_argument("--no-header", dest="no_header", action="store_true", default=False,
                        help="是否隐藏 header 信息；header 信息包含机器名称、当前时间、版本号；"
                             "默认展示 header 信息，配置该参数后 header 信息不再展示；")

    parser.add_argument("--no-title", dest="no_title", action="store_true", default=False,
                        help="是否隐藏 title 信息；title 信息为对当前设备状态值各字段的说明；"
                             "默认展示 title 信息，配置该参数后 title 信息不再展示；")

    parser.add_argument("--use-npu-smi", dest="use_npu_smi", action="store_true", default=True,
                        help="使用命令\"npu-smi info\"获取当前设备状态值；"
                             "注意该命令无法获取到加速卡的实时功率信息；")

    parser.add_argument("--show-power", dest="show_power", action="store_false", default=False,
                        help="是否展示加速卡的功率信息，默认为展示；"
                             "配置了参数 \"--use-npu-smi\" 之后该参数无效；")

    parser.add_argument("--no-compact", dest="no_compact", action="store_true", default=False,
                        help="是否采用紧凑模式展示信息，默认为不采用；"
                             "紧凑模式下会去掉空白行及其他无意义的行，适用于加速卡较多，显示器较小，屏幕显示不下的情况；")

    parser.add_argument("--debug", action="store_true", default=False,
                        help="Debug模式时允许在程序出错的情况下打印更多的调试信息；")
    parser.add_argument("-v", "--version", action="version", version=("npustat version: %s" % __version__))
    args = parser.parse_args()

    # args.use_npu_smi = True
    if check_npu_smi():
        args.use_npu_smi = True

    if args.no_compact:
        args.compact = False
    else:
        args.compact = True
    
    # args.show_power = False  # npu-smi info 命令无法获取到加速卡的功率信息，设置为不展示

    if args.compact:
        args.no_title = True

    if args.interval is None:  # with default value
        args.interval = 2.0  # 默认每2秒刷新一次
    if args.interval > 0:
        args.interval = max(0.1, args.interval)
        if args.json:
            sys.stderr.write("Error: \"--json\" 和 \"-i/--interval/--watch\" 不能同时使用；\n")
            sys.exit(1)

        loop_atlas_stat(**vars(args))
    else:
        del args.interval
        print_atlas_stat(**vars(args))


if __name__ == "__main__":
    main()

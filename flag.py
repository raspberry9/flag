#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
flag는 응용프로그램의 command line argument을 입력 받아서 그 결과를 dictionary로
저장하는 모듈 입니다. 기본적으로 --help 옵션을 제공하며, 버전이 지정된 경우에는
--version 옵션도 제공 됩니다. 예제가 필요한 경우는 이 파일 제일 하단의 테스트 코드를
참조 하세요.

 - 이 코드는 python 2.7.11 버전 에서만 테스트 되었습니다.
 - 개선 요청 및 문의는 koo@kormail.net으로 해주세요.

Copyright (c) 2016, Jaseung Koo.
License: MIT (see LICENSE for details)
"""

from __future__ import with_statement

__author__ = 'Jaseung Koo'
__version__ = '0.0.1'
__license__ = 'MIT'

import sys

class Flag(object):
    '''command line argument parser'''
    def __init__(self, version=None, desc=None):
        self.procname = self.get_procname()
        self.version = version
        self.desc = desc
        self.flags = []
        self.flags = [{'name': 'help', 'desc': 'print this help message and exit', 'default': False}]
        if self.version:
            self._max_flag_len = 7
            self.flags.append({'name': 'version', 'desc': 'print version and exit', 'default': False})
        else:
            self._max_flag_len = 4
        self.values = {}

    def get_procname(self):
        '''현재 실행중인 프로세스의 이름 중 확장자(.py or .exe)를 제거한 이름을 리턴 합니다.'''
        procname = sys.argv[0].split('/')[-1]
        if procname.endswith('.py'):
            procname = procname[0:-3]
        elif procname.endswith('.exe'):
            procname = procname[0:-4]
        return procname

    def get_default(self, flag):
        '''flag의 기본값을 리턴합니다.'''
        for f in self.flags:
            if f['name'] == flag:
                return f['default']
        return None

    def parse(self):
        '''command line argument를 파싱 하거나 --help나 --version 옵션을 처리하고 종료 합니다.'''
        if len(sys.argv) > 1:
            if '--help' in sys.argv[1:]:
                self.show_help_message()
                sys.exit(0)
            if self.version and '--version' in sys.argv[1:]:
                self.show_version(True)
                sys.exit(0)

        args = self._parse_args()
        arg_names = args.keys()
        optional, required = self._split_flags()
        
        error = [x for x in required if x not in arg_names]
        if error:
            self._show_error_and_exit("Required argument '%s' not found" % (self._dash_flag(error[0]),))

        for arg in arg_names:
            if arg not in optional and arg not in required:
                self._show_error_and_exit("No such option '%s'" % (self._dash_flag(arg),))

        for key, value in args.iteritems():
            self.values[key] = value

        return self.values

    def show_help_message(self):
        '''--help 옵션(도움말 출력)을 처리 합니다.'''
        if self.desc:
            print self.desc
            print

        default_flags = '[--help]'
        if self.version:
            default_flags = default_flags + ' [--version]'
        optional, requred = self._split_flags()
        required_str = ' '.join([(self._dash_flag(x)) if isinstance(self.get_default(x), bool) else (self._dash_flag(x) + ' ' + x.upper()) for x in requred if x not in default_flags])
        optional_str = ' '.join([(('[' + self._dash_flag(x) + ']') if isinstance(self.get_default(x), bool) else ('[%s %s]' % (self._dash_flag(x), 'VALUE' if len(x) == 1 else x.upper()))) for x in optional if x not in default_flags])
        options = ''
        if optional_str:
            options = options + ' ' + optional_str
        if required_str:
            options = options + ' ' + required_str
        title_msg = 'usage: %s%s%s' % (self.procname, ' ' + default_flags, options)
        print(title_msg)

        for f in self.flags:
            name = self._dash_flag(f['name'])
            space = ' ' * (self._max_flag_len - len(name)) + '\t'
            print '  %s%s%s%s' % (name, space, f['desc'], '' if not f['default'] else '(default: %s)' % (str(f['default']),))

    def show_version(self, short=False):
        '''--version(버전 출력) 옵션을 처리 합니다.'''
        if short:
            print(self.version)
        else:
            print('%s %s' % (self.procname, self.version))

    def add(self, flag, desc, default=None):
        '''사용자가 필요한 옵션을 추가 합니다.'''
        if len(flag) > self._max_flag_len:
            self._max_flag_len = len(flag)
        self.flags.append({'name': flag, 'desc': desc, 'default': default})
        if isinstance(default, bool) or default:
            self.values[flag] = default

    def get(self, flag):
        '''플래그의 값을 리턴 합니다. 해당 플래그가 없는 경우에는 None을 리턴 합니다.'''
        if flag in self.values:
            return self.values[flag]
        return None

    def _get_arg_value(self, default, arg):
        if default:
            if isinstance(default, bool):
                return True
            elif isinstance(default, int):
                return int(arg)
            elif isinstance(default, long):
                return long(arg)
            elif isinstance(default, float):
                return float(arg)
        return str(arg)

    def _parse_args(self):
        args = {}
        flag_names = [x['name'] for x in self.flags]
        key = None
        argv = sys.argv[1:]
        for arg in argv:
            try:
                if arg.startswith('-'):
                    if len(arg) >= 3 and arg[1] != '-':
                        # 1글자 bool 옵션이 두 개 이상 중첩인지 확인
                        single_options = list(arg.replace('-', ''))
                        for f in single_options:
                            if not isinstance(self.get_default(f), bool):
                                self._show_error_and_exit("No such option '%s'" % (arg,))
                        [argv.append('-' + x) for x in single_options[1:]]
                        arg = '-' + single_options[0]

                    key = arg.replace('-', '').split('=')[0]
                    if key not in flag_names:
                        self._show_error_and_exit("No such option '%s'" % (arg,))
                    if '=' in arg:
                        if isinstance(self.get_default(key), bool):
                            self._show_error_and_exit('Invalid value for %s' % (self._dash_flag(key),))
                        else:
                            args[key] = self._get_arg_value(self.get_default(key), arg.replace('-', '').split('=')[1])
                    else:
                        if isinstance(self.get_default(key), bool):
                            args[key] = True
                        continue
                else:
                    if key is None:
                        self._show_error_and_exit("No such option '%s'" % (arg,))
                    if isinstance(self.get_default(key), bool):
                        self._show_error_and_exit('Invalid value for %s' % (self._dash_flag(key),))
                    args[key] = self._get_arg_value(self.get_default(key), arg)
            except ValueError:
                self._show_error_and_exit('Invalid value for %s' % (arg,))
        return args

    def _split_flags(self):
        optional = []
        required = []
        for f in self.flags:
            if f['default'] is None:
                required.append(f['name'])
            else:
                optional.append(f['name'])
        return optional, required

    def _dash_flag(self, flag):
        if not flag.startswith('-'):
            return '-' + flag if len(flag) == 1 else '--' + flag
        return flag

    def _show_error_and_exit(self, message):
        self.desc = message
        self.show_help_message()
        sys.exit(0)

if __name__ == '__main__':
    # 1. 객체를 생성합니다.
    test_flag = Flag(version='1.0', desc='flag 모듈을 테스트 하는 앱입니다.')
    #  version 키워드 인자를 생략하면 --version 명령은 사용할 수 없습니다.
    # test_flag = Flag(version='1.0', desc='flag 모듈을 테스트 하는 앱입니다.')
    
    # 2. 사용자 정의 옵션을 아래와 같이 추가해 줍니다.
    test_flag.add('debug', '이 옵션이 있으면 True, 생략되면 False가 됩니다.', False)
    test_flag.add('host', '값이 str 타입인 옵션 입니다.', 'localhost')
    test_flag.add('port', '값이 숫자 타입인 옵션 입니다.', 8080)
    test_flag.add('must', '이 옵션은 기본값이 없으므로 반드시 값을 입력해야 합니다.')
    test_flag.add('a', '한 글자 옵션의 경우는 --[옵션] 대신 -[옵션]으로 입력해야 합니다.', 10)
    test_flag.add('b', '한 글자 옵션 중 bool 변수들은 하나의 옵션에 넣을 수 있습니다.', False)
    test_flag.add('c', '예를 들어 -bc와 같이 넣으면 -b -c와 동일한 결과가 됩니다.', False)
    
    # 3. 옵션을 파싱합니다.
    test_flag.parse()
    
    # 4. 필요한 곳에서 값을 사용 합니다.
    print '* 입력한 옵션 *'
    for k, v in test_flag.values.iteritems():
        print '  - %s: %s' % (k, v)
    
    # test_flag.get('a') 처럼 get 함수로 사용할 수도 있습니다.

    # 아래와 같이 실행해 보세요.
    # --must 옵션이 없으므로 오류
    # python flag.py -a=1

    # 도움말 출력
    # python flag.py --help

    # 버전 출력
    # python flag.py --version

    # 여러가지 옵션
    # python flag.py --must 1 --debug
    # python flag.py --must 2 --host=127.0.0.1 --port=12345
    # python flag.py --must 3 --host localhost
    # python flag.py --must 4 -a 50
    # python flag.py --must 5 -bc

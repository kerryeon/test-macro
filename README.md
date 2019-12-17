# TestMacro - a test automating library written in Python
[![travis-ci](https://travis-ci.org/kerryeon/test-macro.svg?branch=master)](https://travis-ci.org/kerryeon/test-macro)
[![coveralls](https://coveralls.io/repos/github/kerryeon/test-macro/badge.svg?branch=master)](https://coveralls.io/github/kerryeon/test-macro?branch=master)

Do not change the experimental conditions one by one!

TestMacro is a module that fully / semi-automates the testing and recording of results in programs.

TestMacro can:
* [x] Change `.yaml`
* [ ] Change arguments
* [x] Recode programs
* [ ] `.csv` records
* [ ] Label arguments
* [ ] Write meta file

## Install TestMacro
```bash
$ pip install test-macro
```

## Hello world
1. Get your own program, setting files.
2. Create `case.yml` in the path you want to execute.
```yml
%YAML:1.0

exes:
- ./program

cases:
- my-settings.yaml:
  - my_var1: (3, 10)  # 3, 4, ..., 10
  - my_var2: 2 ** (0, 3)  # 1, 2, 4, 8
  - my_var3:
    - my_string1
    - my_string2

for:
- record: My GUI Title
```
3. type `macro` in the path containing `case.yml`.

# List of main features
TODO

# License
TestMacro uses the [MIT license](https://github.com/kerryeon/test-macro/blob/master/LICENSE).

(The standalone tool is under GPL2)

# Contribute
TestMacro is currently determining a pull-requests policy.

If you would like to contribute now, please contact below.

# Contact
If you have any questions or want my assistance, you can email me at ho.kim at gnu ac kr.

* [Ho Kim](https://github.com/kerryeon)

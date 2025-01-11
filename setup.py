from setuptools import setup, find_packages
from recKeyMouse.version import VERSION

setup(
    name="KeyMouseRecorder",
    version=VERSION,
    author="Mengxun Li",
    author_email="mengxunli@whu.edu.cn",
    description="A screen action recorder",

    # 项目主页
    url="https://github.com/MenxLi/RecKeyMouse", 

    classifiers = [
        #   Development Status
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],

    python_requires=">=3.5",

    packages=find_packages(),
    exclude_package_data={'': ["conf.json"]},
    include_package_data = True,

    install_requires = ["pynput", "PyQt6", "platformdirs"],

    entry_points = {
        "console_scripts":[
            "reckm=recKeyMouse.exec:main",
        ]
    }
)
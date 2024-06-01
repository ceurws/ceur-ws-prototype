from setuptools import setup, find_packages

setup(
    name = 'ceur_ws_workshops',
    version = '0.1',
    description = "Submission process for the CEUR-WS.org workshop proceedings",
    author = "Filip Muntean, Hein Kolk",
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'asgiref==3.8.1',
        'crispy-bootstrap4==2024.1',
        'DateTime==5.5',
        'Django==5.0.6',
        'django-countries==7.6.1',
        'django-crispy-forms==2.1',
        'imageio==2.34.1',
        'lazy-loader==0.4',
        'networkx==3.3',
        'numpy==1.26.4',
        'opencv-python==4.9.0.80',
        'packaging==24.0',
        'pillow==10.3.0',
        'pip==24.0',
        'pytz==2024.1',
        'scikit-image==0.23.2',
        'scipy==1.13.1',
        'setuptools==70.0.0',
        'signature-detect==0.1.4',
        'sqlparse==0.5.0',
        'tifffile==2024.5.22',
        'typing-extensions==4.12.0',
        'Wand==0.6.13',
        'zope.interface==6.4.post2',
        'wheel'
    ],
    entry_points = {
        'console_scripts': [
            'ceur_ws_workshops_manage = ceur_ws_workshops.manage:main',
        ],
    },

    classifiers = [ 
        'Framework :: Django',
        'Framework :: Django :: 3.0', 
    ],

)
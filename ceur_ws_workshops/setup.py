from setuptools import setup, find_packages

setup(
    name = 'ceur_ws_workshops',
    version = '0.2',
    description = "Submission process for the CEUR-WS.org workshop proceedings",
    author = "Filip Muntean, Hein Kolk",
    packages = find_packages(),
    include_package_data = True,
    install_requires = [        
        'asgiref==3.8.1',
        'crispy-bootstrap4==2024.1',
        'Django==5.0.6',
        'django-countries==7.6.1',
        'django-crispy-forms==2.1',
        'pip==24.0',
        'setuptools==70.0.0',
        'sqlparse==0.5.0',
        'typing_extensions==4.12.1',
        'wheel==0.43.0',
        'openreview-py==1.39.7',
        'PyPDF2==3.0.1',
    ],
    python_requires='>=3.10',
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
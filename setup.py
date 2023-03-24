from setuptools import setup
  
setup(
    name='nifti2dicom',
    version='0.1.1',
    description='Package translate nifti to dicom files',
    author='Dominik Becker',
    author_email='dominik.becker1@uni-goettingen.de',
    packages=['nifti2dicom'],
    install_requires=[
        'argparse',
        'pydicom',
        'numpy',
        'nibabel'
    ],
)
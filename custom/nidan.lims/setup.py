from setuptools import find_packages, setup


setup(
    name="nidan.lims",
    version="0.1.0",
    description="NIDAN Pathology Lab customization for SENAITE LIMS",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"nidan.lims": ["*.zcml"]},
    install_requires=["senaite.lims"],
    entry_points={
        "z3c.autoinclude.plugin": ["target = plone"],
    },
)

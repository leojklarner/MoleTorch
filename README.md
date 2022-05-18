[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>


<p align="left">
  <a href="https://github.com/leojklarner/gauche">
    <img src="imgs/gauche_logo.png" width="45%" />
    <img src="imgs/gauche.gif" width="22%" hspace="30"/>
  </a>
</p>

A Gaussian Process Library for Molecules, Proteins and Reactions. 



## Install

We recommend using a conda virtual environment.

```
conda create -n gprotorch python=3.8
conda activate gprotorch
pip install gpytorch botorch
pip install scikit-learn pandas pytest tqdm jupyter
conda install -c conda-forge rdkit
```

Optional for running tests.

```
pip install gpflow grakel
```


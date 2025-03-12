# PyTorchFire: A GPU-Accelerated Wildfire Simulator with Differentiable Cellular Automata


[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![PyPI - Version](https://img.shields.io/pypi/v/pytorchfire)](https://pypi.org/project/pytorchfire/)
[![Read the Docs](https://readthedocs.org/projects/pytorchfire/badge/)](https://pytorchfire.readthedocs.io/)

[![Paper doi](https://img.shields.io/badge/Paper%20DOI-10.1016%2Fj.envsoft.2025.106401-blue)](https://doi.org/10.1016/j.envsoft.2025.106401)
[![Paper license](http://mirrors.creativecommons.org/presskit/buttons/80x15/svg/by.svg)](http://creativecommons.org/licenses/by/4.0/)

[![Code DOI](https://img.shields.io/badge/Code_DOI-10.5281%2Fzenodo.13132218-blue)](https://doi.org/10.5281/zenodo.13132218)
[![Dataset DOI](https://img.shields.io/badge/Dataset_DOI-10.17632%2Fnx2wsksp9k.1-blue)](https://doi.org/10.17632/nx2wsksp9k.1)

## About The Project

Accurate and rapid prediction of wildfire trends is crucial for effective management and mitigation. However, the stochastic nature of fire propagation poses significant challenges in developing reliable simulators. In this paper, we introduce PyTorchFire, an open-access, PyTorch-based software that leverages GPU acceleration. With our redesigned differentiable wildfire Cellular Automata (CA) model, we achieve millisecond-level computational efficiency, significantly outperforming traditional CPU-based wildfire simulators on real-world-scale fires at high resolution. Real-time parameter calibration is made possible through gradient descent on our model, aligning simulations closely with observed wildfire behavior both temporally and spatially, thereby enhancing the realism of the simulations. Our PyTorchFire simulator, combined with real-world environmental data, demonstrates superior generalizability compared to supervised learning surrogate models. Its ability to predict and calibrate wildfire behavior in real-time ensures accuracy, stability, and efficiency. PyTorchFire has the potential to revolutionize wildfire simulation, serving as a powerful tool for wildfire prediction and management.

## Getting Started
### Notebook Examples

- Wildfire Prediction: [examples/prediction.ipynb](examples/prediction.ipynb) [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/xiazeyu/PyTorchFire/blob/main/examples/prediction.ipynb)
- Parameter Calibration: [examples/calibration.ipynb](examples/calibration.ipynb) [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/xiazeyu/PyTorchFire/blob/main/examples/calibration.ipynb)

### Installation

Install with minimal dependencies:

```shell
pip install pytorchfire
```

Install with dependencies for examples:

```shell
pip install 'pytorchfire[examples]'
```

### Quick Start

To perform wildfire prediction:

```python
from pytorchfire import WildfireModel

model = WildfireModel() # Create a model with default parameters and environment data
model = model.cuda() # Move the model to GPU
# model.reset(seed=seed) # Reset the model with a seed
for _ in range(100): # Run the model for 100 steps
    model.compute() # Compute the next state
```

To perform parameter calibration:

```python
import torch
from pytorchfire import WildfireModel, BaseTrainer

model = WildfireModel()

trainer = BaseTrainer(model)

trainer.train()
trainer.evaluate()
```

## API Documents

See at Our [Read the Docs](https://pytorchfire.readthedocs.io/).

## Dataset

See at Our [Dataset](https://doi.org/10.17632/nx2wsksp9k.1).

## Reference

```bibtex
@article{xia2025pytorchfire,
 author = {Zeyu Xia and Sibo Cheng},
 copyright = {CC BY 4.0},
 doi = {10.1016/j.envsoft.2025.106401},
 issn = {1364-8152},
 journal = {Environmental Modelling & Software},
 keywords = {Wildfire simulation, Differentiable Cellular Automata, PyTorch-based software, Parallel computing techniques, GPU-acceleration},
 language = {English},
 month = {4},
 pages = {106401},
 title = {PyTorchFire: A GPU-accelerated wildfire simulator with Differentiable Cellular Automata},
 url = {https://www.sciencedirect.com/science/article/pii/S1364815225000854},
 volume = {188},
 year = {2025}
}
```

## License

MIT License. More information see [LICENSE](./LICENSE)

## Contact

Zeyu Xia - [zeyu.xia@virginia.edu](mailto:zeyu.xia@virginia.edu)

Sibo Cheng - [sibo.cheng@enpc.fr](mailto:sibo.cheng@enpc.fr)

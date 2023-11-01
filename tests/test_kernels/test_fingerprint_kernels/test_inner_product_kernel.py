"""
Test suite for Inner product kernel.
"""

import pytest
import torch
from gpytorch.kernels import ScaleKernel
from gauche.kernels.fingerprint_kernels.inner_product_kernel import (
    batch_inner_product_sim,
    InnerProductKernel,
)

tkwargs = {"dtype": torch.double}


@pytest.mark.parametrize(
    "x1, x2",
    [
        (torch.ones((2, 2), **tkwargs), torch.ones((2, 2), **tkwargs)),
    ],
)
def test_inner_product_similarity_with_equal_inputs(x1, x2):
    """Test the Inner Product similarity metric between two equal input tensors."""
    similarity = batch_inner_product_sim(x1, x2)
    assert torch.isclose(similarity, 2 * torch.ones((2, 2), **tkwargs)).all()


def test_inner_product_similarity_with_unequal_inputs():
    """Test the Inner Product similarity metric between two unequal input tensors."""
    x1 = torch.tensor([1, 0, 1, 1], **tkwargs)
    x2 = torch.tensor([1, 1, 0, 0], **tkwargs)
    # Add a batch dimension
    x1 = x1[None, :]
    x2 = x2[None, :]
    similarity = batch_inner_product_sim(x1, x2)

    assert torch.allclose(similarity, torch.tensor(1.0, **tkwargs))


def test_inner_product_kernel():
    """Test the Inner Product kernel when integrated with GP."""

    x = torch.randint(0, 2, (10, 5))
    # Non-batch: Simple option
    covar_module = ScaleKernel(InnerProductKernel())
    covar = covar_module(x)  # Output: LazyTensor of size (10 x 10)
    assert covar.size() == torch.Size([10, 10])
    batch_x = torch.randint(0, 2, (2, 10, 5))
    # Batch: Simple option
    covar_module = ScaleKernel(InnerProductKernel())
    covar = covar_module(batch_x)  # Output: LazyTensor of size (2 x 10 x 10)
    assert covar.size() == torch.Size([2, 10, 10])

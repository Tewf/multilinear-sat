"""How the optimised parameters map to the point p in [-1, 1]^n, and how they stay feasible."""
import torch


def _uniform(shape, generator, scale):
    return (torch.rand(shape, generator=generator, device=generator.device) * 2 - 1) * scale


class TanhRelaxation:
    """Unconstrained theta, p = tanh(theta); nothing to project."""

    def initial_parameters(self, shape, generator, scale):
        return _uniform(shape, generator, scale).requires_grad_(True)

    def point(self, parameters):
        return torch.tanh(parameters)

    def project(self, parameters):
        pass


class BoxRelaxation:
    """FourierSAT's formulation: the point itself is the parameter, kept on the box [-1, 1]^n by
    clipping after every step (projected gradient)."""

    def initial_parameters(self, shape, generator, scale):
        return _uniform(shape, generator, scale).clamp_(-1.0, 1.0).requires_grad_(True)

    def point(self, parameters):
        return parameters

    def project(self, parameters):
        with torch.no_grad():
            parameters.clamp_(-1.0, 1.0)

"""Ascent steps on theta [G, n] whose state can be reset for the groups a Luby restart
reinitialises, so a fresh group does not inherit another's moments."""
import torch


class GroupAdam:
    """Adam with bias correction; first and second moments and the step count are per group."""

    def __init__(self, theta, learning_rate, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.theta, self.learning_rate = theta, learning_rate
        self.beta1, self.beta2, self.epsilon = beta1, beta2, epsilon
        self.first, self.second = torch.zeros_like(theta), torch.zeros_like(theta)
        self.count = torch.zeros(theta.shape[0], 1, device=theta.device)

    def step(self, gradient):
        """theta += lr * corrected first moment / sqrt(corrected second moment): an ascent."""
        self.count += 1
        self.first.mul_(self.beta1).add_(gradient, alpha=1 - self.beta1)
        self.second.mul_(self.beta2).addcmul_(gradient, gradient, value=1 - self.beta2)
        first_hat = self.first / (1 - self.beta1 ** self.count)
        second_hat = self.second / (1 - self.beta2 ** self.count)
        self.theta.add_(self.learning_rate * first_hat / (second_hat.sqrt() + self.epsilon))

    def reset(self, groups):
        if groups:
            self.first[groups], self.second[groups], self.count[groups] = 0.0, 0.0, 0.0


class NaturalStep:
    """theta += lr * g. The direction E_tilted[x] - p is already the natural gradient of the
    exponential family (the Fisher metric removes the (1 - p^2) factors), so nothing else is needed."""

    def __init__(self, theta, learning_rate):
        self.theta, self.learning_rate = theta, learning_rate

    def step(self, gradient):
        self.theta.add_(self.learning_rate * gradient)

    def reset(self, groups):
        pass


OPTIMIZERS = {"adam": GroupAdam, "natural": NaturalStep}


def build_optimizer(name, theta, learning_rate):
    return OPTIMIZERS[name](theta, learning_rate)

"""Ascent steps on theta [G, n] with a decreasing step size per group, eta_t = eta_0 / (1 + t / t_half)
with t the steps since the group's restart: with constant smoothing the cross-entropy iteration
collapses to a unit mass with probability 1 (Costa, Jones, Kroese 2007). The state of a group is
reset when a Luby restart reinitialises it."""
import torch


class PlainStep:
    """theta += eta_t g. The direction E_tilted[x] - p is the plain gradient in the natural
    parameters theta, which to first order is the natural gradient in the means p; information-
    geometric optimisation makes it exact in the means, and for Bernoulli models that is PBIL
    (Ollivier, Arnold, Auger, Hansen 2017). It is not a natural-gradient step in theta."""

    def __init__(self, theta, learning_rate, half_life):
        self.theta, self.learning_rate, self.half_life = theta, learning_rate, half_life
        self.count = torch.zeros(theta.shape[0], 1, device=theta.device)

    def step_size(self):
        return self.learning_rate / (1.0 + self.count / self.half_life)

    def step(self, gradient):
        self.theta.add_(self.step_size() * gradient)
        self.count += 1

    def reset(self, groups):
        if groups:
            self.count[groups] = 0.0


class GroupAdam(PlainStep):
    """Adam with bias correction on the same schedule; first and second moments per group."""

    def __init__(self, theta, learning_rate, half_life, beta1=0.9, beta2=0.999, epsilon=1e-8):
        super().__init__(theta, learning_rate, half_life)
        self.beta1, self.beta2, self.epsilon = beta1, beta2, epsilon
        self.first, self.second = torch.zeros_like(theta), torch.zeros_like(theta)

    def step(self, gradient):
        self.first.mul_(self.beta1).add_(gradient, alpha=1 - self.beta1)
        self.second.mul_(self.beta2).addcmul_(gradient, gradient, value=1 - self.beta2)
        first_hat = self.first / (1 - self.beta1 ** (self.count + 1))
        second_hat = self.second / (1 - self.beta2 ** (self.count + 1))
        self.theta.add_(self.step_size() * first_hat / (second_hat.sqrt() + self.epsilon))
        self.count += 1

    def reset(self, groups):
        if groups:
            super().reset(groups)
            self.first[groups], self.second[groups] = 0.0, 0.0


OPTIMIZERS = {"adam": GroupAdam, "plain": PlainStep}


def build_optimizer(name, theta, learning_rate, half_life):
    return OPTIMIZERS[name](theta, learning_rate, half_life)

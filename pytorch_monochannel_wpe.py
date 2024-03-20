import torch
import torch.nn.functional as F

def build_y_tilde(Y, taps, delay):
    conv_kern = torch.fliplr(torch.eye(taps, dtype=torch.complex128)).unsqueeze(-2)
    return F.conv1d(Y.unsqueeze(-2), conv_kern, padding=delay+taps-1)[..., :Y.shape[-1]]

def get_power_inverse(signal):
    power = signal.real ** 2 + signal.imag ** 2
    eps = 1e-10 * torch.max(power)
    inverse_power = 1 / torch.maximum(power, eps)
    return inverse_power

def wpe_dev(Y, taps=10, delay=3, iterations=3):
    Y_tilde = build_y_tilde(Y, taps, delay)
    X = Y
    for iteration in range(iterations):
        inverse_power = get_power_inverse(X)
        Y_tilde_inverse_power = Y_tilde * inverse_power[..., None, :]
        R = torch.matmul(Y_tilde_inverse_power, Y_tilde.transpose(-2, -1).conj())
        P = torch.matmul(Y_tilde_inverse_power, Y[..., None].conj())
        G = torch.linalg.solve(R, P)
        X = Y - torch.matmul(G.transpose(-2, -1).conj(), Y_tilde).squeeze(-2)
    return X

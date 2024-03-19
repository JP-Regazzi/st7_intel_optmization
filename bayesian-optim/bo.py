import numpy as np
import GPy
from scipy.optimize import minimize
from scipy.stats import norm

class PRBO:
    def __init__(self, f, bounds, discrete_dims, kernel=None, noise_var=1e-5):
        self.f = f
        self.bounds = bounds
        self.discrete_dims = discrete_dims
        self.kernel = kernel or GPy.kern.RBF(input_dim=len(bounds))
        self.noise_var = noise_var
        self.X = []
        self.Y = []
        self.model = None

    def expected_improvement(self, x, z_samples):
        if not self.model:
            return 0
        
        y_best = np.max(self.Y)
        mu, var = self.model.predict(np.hstack((np.tile(x, (z_samples.shape[0], 1)), z_samples)))
        std = np.sqrt(var)
        
        Z = (mu - y_best) / std
        ei = (mu - y_best) * norm.cdf(Z) + std * norm.pdf(Z)
        return np.mean(ei)

    def sample_discrete(self, z_prob):
        z_samples = np.zeros((z_prob.shape[1], len(self.discrete_dims)), dtype=int)
        for i, d in enumerate(self.discrete_dims):
            z_samples[:, i] = np.array([d[np.argmax(p[:len(d)])] for p in z_prob[i]])
        return z_samples

    def optimize_af(self, n_samples=1000, n_restarts=10):
        x_opt, z_prob_opt, ei_opt = None, None, -np.inf
        
        for _ in range(n_restarts):
            x = np.random.rand(len(self.bounds))
            z_prob_indices = np.array([np.random.choice(len(d), size=n_samples, p=np.random.dirichlet(np.ones(len(d)))) for d in self.discrete_dims])
            z_prob = np.zeros((len(self.discrete_dims), n_samples, max(len(d) for d in self.discrete_dims)))
            for i, d in enumerate(self.discrete_dims):
                z_prob[i, np.arange(n_samples), z_prob_indices[i]] = 1
            
            def objective(params):
                x, z_prob = params[:-n_samples*len(self.discrete_dims)], params[-n_samples*len(self.discrete_dims):]
                z_prob = z_prob.reshape(len(self.discrete_dims), n_samples, -1)
                z_samples = self.sample_discrete(z_prob)
                return -self.expected_improvement(x, z_samples)
            
            params0 = np.concatenate((x, z_prob.flatten()))
            result = minimize(objective, params0, bounds=[(0, 1)] * len(params0))
            
            if -result.fun > ei_opt:
                x_opt, z_prob_opt, ei_opt = result.x[:-n_samples*len(self.discrete_dims)], result.x[-n_samples*len(self.discrete_dims):].reshape(z_prob.shape), -result.fun
        
        return x_opt, z_prob_opt, ei_opt

    def optimize(self, n_iter=20):
        for _ in range(n_iter):
            if not self.model:
                x = np.random.rand(len(self.bounds))
                z = [np.random.choice(d) for d in self.discrete_dims]
            else:
                x, z_prob, _ = self.optimize_af()
                z = self.sample_discrete(z_prob)[0]
            
            y = self.f(np.hstack((x, z)))
            self.X.append(np.hstack((x, z)))
            self.Y.append(y)
            
            if len(self.X) > 1:
                self.model = GPy.models.GPRegression(np.array(self.X), np.array(self.Y).reshape(-1, 1), kernel=self.kernel, noise_var=self.noise_var)
                self.model.optimize()
        
        best_idx = np.argmax(self.Y)
        return self.X[best_idx], self.Y[best_idx]
    
def mixed_func(params):
    x = params[0]
    z1 = int(params[1])
    z2 = int(params[2])
    return -((x - 0.5) ** 2 + (z1 - 1) ** 2 + (z2 - 2) ** 2)

bounds = [(0, 1)]
discrete_dims = [[0, 1, 2], [0, 1, 2, 3]]

optimizer = PRBO(mixed_func, bounds, discrete_dims)
best_params, best_value = optimizer.optimize(n_iter=20)

print(f"Best parameters found: {best_params}")
print(f"Best function value: {best_value}")
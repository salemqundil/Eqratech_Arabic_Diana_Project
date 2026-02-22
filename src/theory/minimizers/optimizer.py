# theory/minimizers/optimizer.py
# -*- coding: utf-8 -*-
"""
Robust optimizer with grid fallback
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Optional, List


@dataclass
class OptimResult:
    V_star: Optional[np.ndarray]
    E_min: float
    success: bool
    n_iters: int = 0
    method: str = ""


class VowelOptimizer:
    def __init__(self, energy, V_space):
        self.energy = energy
        self.V_space = V_space
        self.max_iters = 400
        self.tol = 1e-8
        self.lr0 = 0.08
        self.backtrack = 0.5
        self.min_lr = 1e-6
        self.grid_n = 81
        self.local_refine_steps = 60

    def _bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        if hasattr(self.V_space, 'triangle_k'):
            k = self.V_space.triangle_k
            return np.array([-k, -k]), np.array([k, k])
        return np.array([-1.0, -1.0]), np.array([1.0, 1.0])

    def _project(self, V: np.ndarray) -> np.ndarray:
        lo, hi = self._bounds()
        return np.minimum(np.maximum(V, lo), hi)

    def _random_starts(self, n: int) -> List[np.ndarray]:
        lo, hi = self._bounds()
        rng = np.random.default_rng(42)
        pts = [rng.uniform(lo, hi) for _ in range(n)]
        pts.append((lo + hi) / 2.0)
        return pts

    def _grad(self, V: np.ndarray, C_L: np.ndarray, C_R: np.ndarray, flags: Dict) -> np.ndarray:
        if hasattr(self.energy, 'gradient'):
            return self.energy.gradient(V, C_L, C_R, flags)
        eps = 1e-6
        g = np.zeros_like(V, dtype=float)
        base = self.energy(V, C_L, C_R, flags)
        for i in range(len(V)):
            d = np.zeros_like(V, dtype=float)
            d[i] = eps
            g[i] = (self.energy(self._project(V + d), C_L, C_R, flags) - base) / eps
        return g

    def _solve_gd(self, V0: np.ndarray, C_L: np.ndarray, C_R: np.ndarray, flags: Dict) -> OptimResult:
        V = self._project(np.array(V0, dtype=float))
        E_prev = self.energy(V, C_L, C_R, flags)
        lr = self.lr0
        
        for it in range(1, self.max_iters + 1):
            g = self._grad(V, C_L, C_R, flags)
            if np.linalg.norm(g) < self.tol:
                return OptimResult(V, E_prev, True, it, method="gd")
            
            success_step = False
            for _ in range(20):
                V_new = self._project(V - lr * g)
                E_new = self.energy(V_new, C_L, C_R, flags)
                if np.isfinite(E_new) and E_new <= E_prev - 1e-12:
                    V, E_prev = V_new, E_new
                    success_step = True
                    break
                lr *= self.backtrack
                if lr < self.min_lr:
                    break
            
            if not success_step:
                return OptimResult(None, float("inf"), False, it, method="gd_failed")
        
        return OptimResult(None, float("inf"), False, self.max_iters, method="gd_maxiter")

    def _grid_search(self, C_L: np.ndarray, C_R: np.ndarray, flags: Dict) -> OptimResult:
        lo, hi = self._bounds()
        xs = np.linspace(lo[0], hi[0], self.grid_n)
        ys = np.linspace(lo[1], hi[1], self.grid_n)
        
        best_E = float("inf")
        best_V = None
        
        for x in xs:
            for y in ys:
                V = np.array([x, y], dtype=float)
                if hasattr(self.V_space, 'is_in_vowel_triangle'):
                    if not self.V_space.is_in_vowel_triangle(V):
                        continue
                E = self.energy(V, C_L, C_R, flags)
                if np.isfinite(E) and E < best_E:
                    best_E = E
                    best_V = V.copy()
        
        if best_V is None:
            return OptimResult(None, float("inf"), False, 0, method="grid_failed")
        
        V = best_V
        lr = 0.05
        for k in range(self.local_refine_steps):
            g = self._grad(V, C_L, C_R, flags)
            V2 = self._project(V - lr * g)
            E2 = self.energy(V2, C_L, C_R, flags)
            if np.isfinite(E2) and E2 < best_E:
                best_E, V = E2, V2
            else:
                lr *= 0.7
                if lr < 1e-6:
                    break
        
        return OptimResult(V, best_E, True, self.local_refine_steps, method="grid+refine")

    def solve_numerical(self, C_L: np.ndarray, C_R: np.ndarray, flags: Dict) -> Tuple[np.ndarray, float, bool]:
        starts = self._random_starts(n=8)
        best = OptimResult(None, float("inf"), False, 0, method="none")
        
        for s in starts:
            res = self._solve_gd(s, C_L, C_R, flags)
            if res.success and res.E_min < best.E_min:
                best = res
        
        if best.success and best.V_star is not None:
            return best.V_star, float(best.E_min), True
        
        res2 = self._grid_search(C_L, C_R, flags)
        if res2.success and res2.V_star is not None:
            return res2.V_star, float(res2.E_min), True
        
        return np.array([0.0, 0.0]), float("inf"), False

    def verify_uniqueness(self, C_L: np.ndarray, C_R: np.ndarray, flags: Dict, n_trials: int = 20) -> Tuple[bool, float]:
        sols = []
        for s in self._random_starts(n_trials):
            V, _, ok = self.solve_numerical(C_L, C_R, flags)
            if ok:
                sols.append(V)
        
        if len(sols) < 2:
            return True, 0.0
        
        max_dev = 0.0
        for i in range(len(sols)):
            for j in range(i + 1, len(sols)):
                max_dev = max(max_dev, float(np.linalg.norm(sols[i] - sols[j])))
        
        return (max_dev < 1e-2), max_dev
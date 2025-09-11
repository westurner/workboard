
import numpy as np
import sympy as sy

import pytest
import unittest
Test = unittest.TestCase()


def linspace_rational(start, stop, num: int = 50, endpoint: bool = True, retstep=False, dtype=None, axis=0):
    """
    Return num evenly spaced samples, calculated as sympy.Rational, over the interval [start, stop]
    Works like numpy.linspace but returns a list of sympy.Rational.
    """
    if num < 1:
        raise ValueError("num must be >= 1")
    start = sy.Rational(start)
    stop = sy.Rational(stop)
    if num == 1:
        points = [start]
        step = None
    if num == 2 and endpoint:
        points = [start, stop]
        step = None
    else:
        if endpoint:
            div = (num - 1)
            step = (stop - start) / div  # type: ignore
            points = [*(start + (step * i) for i in range(div)), stop]  # type: ignore
        else:
            div = num
            step = (stop - start) / div  # type: ignore
            points = [start + (step * i) for i in range(num)]  # type: ignore

    if dtype is not None and dtype is not sy.Rational:
        # Only support float and int dtypes, like np.linspace
        try:
            dtype_type = np.dtype(dtype).type
        except Exception:
            raise ValueError(f"Unsupported dtype: {dtype}")
        if dtype_type is int:
            points = [int(p) for p in points]
        elif dtype_type is float:
            points = [float(p) for p in points]
        else:
            raise ValueError(f"Only int and float dtypes are supported, got {dtype}")

    if retstep:
        return points, step
    return points



test_cases = [

    [
        [1, 2],
        (1, 2, 2),
        None
    ],

    [
        [1, 2, 3],
        (1, 3, 3),
        None
    ],
    [
        [1, 2],
        (1, 3, 2),
        dict(endpoint=False),
    ],
    [
        [0, 1, 2, 3],
        (0, 3, 4),
        None
    ],
    [
        [0, 1, 2],
        (0, 3, 3),
        dict(endpoint=False),
    ],
    [
        [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
        (0, 5, 11),
        None
    ],
]
@pytest.mark.parametrize('output_expected, args, kwargs', test_cases)
def test_linspace_rational(output_expected, args, kwargs):
    kwargs = kwargs if kwargs else {}
    output_nplinspa = np.linspace(*args, **kwargs)
    output_thisfunc = linspace_rational(*args, **kwargs)

    #Test.assertEqual(output_expected, output_nplinspa)
    np.testing.assert_allclose(output_expected, output_nplinspa)
    
    np.testing.assert_allclose(output_expected, [float(n) for n in output_thisfunc])  # type: ignore
    #Test.assertEqual(output_expected, output_thisfunc)
    #assert output_expected == output_thisfunc

    # assert expected == np_output
    # assert expected == this_output


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main(['-v', '-l', __file__]))

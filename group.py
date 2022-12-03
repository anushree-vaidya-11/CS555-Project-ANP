from random import randint, randrange   

MAX_INT64 =  9223372036854775807
MIN_INT64 = -9223372036854775808

def mod(n, Q=None):
    '''Keeps n inside the finite ring. That is:
         - If we're in a prime ring (Q is the prime size), modulo it by Q
         - If we're in the int64 ring, do the normal int64 overflow behavior
           (we need to explicitly overflow since Python3 ints are unbounded)
    '''
    if Q is not None: return n % Q
    return (n + MAX_INT64 + 1) % 2**64 - (MAX_INT64 + 1) 
    
def rand_element(Q=None):
    '''Generates a random int64, or a random integer [0, Q) if Q is specified.
       i.e. an element of the int64 ring, or the size-Q prime ring.'''
    if Q is not None: return randrange(Q)
    return randint(MIN_INT64, MAX_INT64)

def assert_is_element(n, Q=None):
    '''Assert that n is a valid int64, or a valid integer mod Q, if Q is provided.'''
    val = n if isinstance(n, int) else n.value
    if Q is None: 
        assert MIN_INT64 <= val <= MAX_INT64, f'{n} is not an int64 and cannot be reconstructed. Use a smaller value.'
    else:
        assert 0 <= val < Q, f'{n} does not fit inside a size-{Q} prime ring, so it cannot be split into shares that can be reconstructed. Use a larger Q or a smaller value.'

PRECISION = 8
MAX_FLOAT = MAX_INT64 / 10**PRECISION  
MIN_FLOAT = MIN_INT64 / 10**PRECISION  

def fixed_point(fl):
    '''Converts a float to an fixed point int, with PRECISION decimal points of precision.'''
    assert MIN_FLOAT < fl < MAX_FLOAT
    return int(fl * 10**PRECISION)

def float_point(n, n_mults=0):
    '''Converts a fixed point integer to a float.
       n_mults is the number of multiplications that generated the int, since multiplications
       of fixed point integers will accumulate extra scaling factors.'''
    scale_factor = (10**PRECISION)**n_mults
    return n / 10**PRECISION / scale_factor
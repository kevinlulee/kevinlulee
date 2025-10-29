from __future__ import annotations
import kevinlulee as kx

def autopath(func: Callable) -> Callable:
    """
    Decorator that auto-supplies dst_path and does path expansion on src_path.
    
    - Expands src_path using Path.expanduser()
    - Auto-generates dst_path if not provided (adds '_output' before extension)
    - Works with src_path and dst_path in any position (positional or keyword args)
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    
    # Find the positions of src_path and dst_path parameters
    src_idx = params.index('src_path') if 'src_path' in params else None
    dst_idx = params.index('dst_path') if 'dst_path' in params else None
    
    if src_idx is None:
        raise ValueError(f"Function {func.__name__} must have a 'src_path' parameter")
    if dst_idx is None:
        raise ValueError(f"Function {func.__name__} must have a 'dst_path' parameter")
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Bind arguments to get actual values
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        
        # Get src_path value
        if 'src_path' in bound.arguments:
            src_path = bound.arguments['src_path']
        else:
            # src_path wasn't provided at all
            raise TypeError(f"{func.__name__} missing required argument: 'src_path'")
        
        # Expand src_path
        src_path = kx.path_expand(src_path)
        
        # Handle dst_path
        if 'dst_path' not in bound.arguments or bound.arguments['dst_path'] is None:
            # Auto-generate dst_path
            dst_path = kx.path_join('~/scratch/temp/temp', kx.get_extension(src_path))
        else:
            dst_path = Path(bound.arguments['dst_path']).expanduser()
        
        # Update bound arguments
        bound.arguments['src_path'] = str(src_path)
        bound.arguments['dst_path'] = str(dst_path)
        
        # Call the function with updated arguments
        value = func(*bound.args, **bound.kwargs)

        if value:
            kx.webbrowser.open(dst_path)
            return value
    
    return wrapper

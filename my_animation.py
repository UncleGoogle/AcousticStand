from matplotlib import animation


class FuncAnimation(animation.FuncAnimation):
    ''' Helper class that overcome an animation bug.
    It seems that the _blit_clear method of the Animation
    class contains an error in several matplotlib verions
    This is newer git version of the function.
    '''
    def _blit_clear(self, artists, bg_cache):
        # Get a list of the axes that need clearing from the artists that
        # have been drawn. Grab the appropriate saved background from the
        # cache and restore.
        axes = set(a.axes for a in artists)
        for a in axes:
            if a in bg_cache:  # this is the previously missing line
                a.figure.canvas.restore_region(bg_cache[a])

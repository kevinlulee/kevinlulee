def matplotopen():
    import matplotlib.pyplot as plt
    fig = plt.gcf()
    fig.savefig('/home/kdog3682/scratch/temp.png')
    plt.close(fig)
    webbrowser.open('/home/kdog3682/scratch/temp.png')

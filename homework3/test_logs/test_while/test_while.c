int f(int y) {
    int x = 0;

    while (x < 3) {
        x++;
    }

    // this should simplify to y < 3
    if (y < x) { 
        return 1;
    
    }

    return 0;
}
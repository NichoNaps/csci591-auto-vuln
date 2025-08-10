int f(int x, int y) {

    if (x > y) {
        x = x + y;
        y = x - y;
        x = x - y;
    } else {
        int y = y++; // variable shadow
        x = y;

        return 1;
    }


    return 0;
}
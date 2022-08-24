package mustshop.arduino.armforarc;

public interface CoordinateToBePlayedInterface {
    public void play(int index);
    public void notifyToggledMenu(int index);
    public int getCurrentlyOpened();
    public int whosBeingEdited();
    public int whichOneBeingPlayedRn();
    public void setBeingEdited(int index);

    void remove(int positionReal);
    void slide(int index, int direction);
    public boolean areWePlaying();
}


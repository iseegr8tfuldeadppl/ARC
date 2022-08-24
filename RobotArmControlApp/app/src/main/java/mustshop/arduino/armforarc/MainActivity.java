package mustshop.arduino.armforarc;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.RecyclerView;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.TextView;
import java.io.IOException;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import mustshop.arduino.arm.R;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;


public class MainActivity extends AppCompatActivity implements CoordinateToBePlayedInterface {

    private RecyclerView coordinatesRecyclerView;
    private Context context;
    private List<Coordinate> coordinates = new ArrayList<>();
    private CoordinateListAdapter coordinateListAdapter;
    private List<TextView> seekBarIndicators = new ArrayList<>();
    private Thread thread;
    private boolean running = true;
    private boolean updated = true;
    private int bottom = 90, spine = 90, tilt = 90, mouth = 90, gate = 90;
    private TextView connectionIndicator;
    private boolean connected = false;
    private final Handler handler = new Handler();
    private OkHttpClient client = new OkHttpClient();
    private long previous_ping=0;
    private final static long ping_period = 5000; // 5 seconds
    private LinearLayout emptyCoordinateListIndicatorPage;
    private int currently_expanded_coordinate = -1;
    private TextView controlsAdd, controlsEdit;
    private SeekBar bottomSeekbar, spineSeekbar, tiltSeekbar, mouthSeekbar, gateSeekbar;
    private final static int requestsTimeout = 30;
    private boolean playing = false;
    private TextView playAll, stopPlayAll;
    private SharedPreferences.Editor editor;
    private SharedPreferences prefs;
    private final String MY_PREFS_NAME = "mustshop.arduino.arm";
    private final static int motors = 5;
    private int previous_playing_index;
    private EditText robotIPInput;
    private String robotIP = "";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // DEBUGGING: debugging tools
        Thread.setDefaultUncaughtExceptionHandler(new TopExceptionHandler());

        // ESSENTIALS:
        prefs = getSharedPreferences(MY_PREFS_NAME, MODE_PRIVATE);
        editor = getSharedPreferences(MY_PREFS_NAME, MODE_PRIVATE).edit();
        context = this;
        client = new OkHttpClient.Builder().writeTimeout(requestsTimeout, TimeUnit.SECONDS).build();
        connectionIndicator = findViewById(R.id.connectionIndicator);
        controlsAdd = findViewById(R.id.controlsAdd);
        controlsEdit = findViewById(R.id.controlsEdit);

        robotIPInput = findViewById(R.id.robotIPInput);
        stopPlayAll = findViewById(R.id.stopPlayAll);
        playAll = findViewById(R.id.playAll);

        // load stuff_from_preferences
        robotIP = prefs.getString("robotIP", "");
        if(!robotIP.isEmpty())
            robotIPInput.setText(robotIP);

        robotIPInput.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {}

            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                robotIP = charSequence.toString();
                editor.putString("robotIP", robotIP);
                editor.apply();
            }

            @Override
            public void afterTextChanged(Editable editable) {}
        });

        String coordinatesSaved = prefs.getString("coordinates", "");
        log(coordinatesSaved);
        String[] coordinatesStrings = coordinatesSaved.split(";");
        for(int i=0; i<coordinatesStrings.length; i++){
            String[] coordinateStrings = coordinatesStrings[i].split(",");
            if(coordinateStrings.length>=motors){
                coordinates.add(new Coordinate(){{
                    bottom = Integer.parseInt(coordinateStrings[0]);
                    spine = Integer.parseInt(coordinateStrings[1]);
                    tilt = Integer.parseInt(coordinateStrings[2]);
                    mouth = Integer.parseInt(coordinateStrings[3]);
                    gate = Integer.parseInt(coordinateStrings[4]);
                }});
            }
        }

        String currentPositionSaved = prefs.getString("currentPosition", "");
        String[] currentPositionStrings = currentPositionSaved.split(",");
        if(currentPositionStrings.length>=motors) {
            bottom = Integer.parseInt(currentPositionStrings[0]);
            spine = Integer.parseInt(currentPositionStrings[1]);
            tilt = Integer.parseInt(currentPositionStrings[2]);
            mouth = Integer.parseInt(currentPositionStrings[3]);
            gate = Integer.parseInt(currentPositionStrings[4]);
        }


        // seekbar stuff
        TextView bottomAngleIndicator = findViewById(R.id.bottomAngleIndicator);
        TextView spineAngleIndicator = findViewById(R.id.spineAngleIndicator);
        TextView tiltAngleIndicator = findViewById(R.id.tiltAngleIndicator);
        TextView mouthAngleIndicator = findViewById(R.id.mouthAngleIndicator);
        TextView gateAngleIndicator = findViewById(R.id.gateAngleIndicator);

        bottomSeekbar = findViewById(R.id.bottomSeekbar);
        spineSeekbar = findViewById(R.id.spineSeekbar);
        tiltSeekbar = findViewById(R.id.tiltSeekbar);
        mouthSeekbar = findViewById(R.id.mouthSeekbar);
        gateSeekbar = findViewById(R.id.gateSeekbar);

        bottomAngleIndicator.setText(String.valueOf(bottom));
        spineAngleIndicator.setText(String.valueOf(spine));
        tiltAngleIndicator.setText(String.valueOf(tilt));
        mouthAngleIndicator.setText(String.valueOf(mouth));
        gateAngleIndicator.setText(String.valueOf(gate));

        bottomSeekbar.setProgress(bottom);
        spineSeekbar.setProgress(spine);
        tiltSeekbar.setProgress(tilt);
        mouthSeekbar.setProgress(mouth);
        gateSeekbar.setProgress(gate);

        bottomSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {  @Override public void onStartTrackingTouch(SeekBar seekBar) {} @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            @Override public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                bottomAngleIndicator.setText(String.valueOf(i));
                updated = true;
                bottom = i;
            }
        });
        spineSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {  @Override public void onStartTrackingTouch(SeekBar seekBar) {} @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            @Override public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                spineAngleIndicator.setText(String.valueOf(i));
                updated = true;
                spine = i;
            }
        });
        tiltSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {  @Override public void onStartTrackingTouch(SeekBar seekBar) {} @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            @Override public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                tiltAngleIndicator.setText(String.valueOf(i));
                updated = true;
                tilt = i;
            }
        });
        mouthSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {  @Override public void onStartTrackingTouch(SeekBar seekBar) {} @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            @Override public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                mouthAngleIndicator.setText(String.valueOf(i));
                updated = true;
                mouth = i;
            }
        });
        gateSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {  @Override public void onStartTrackingTouch(SeekBar seekBar) {} @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            @Override public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                gateAngleIndicator.setText(String.valueOf(i));
                updated = true;
                gate = i;
            }
        });


        // coordinate list stuff
        coordinatesRecyclerView = findViewById(R.id.coordinatesRecyclerView);
        coordinateListAdapter = new CoordinateListAdapter(context, coordinates);
        coordinatesRecyclerView.setAdapter(coordinateListAdapter);
        coordinatesRecyclerView.setLayoutManager(new MyLinearLayoutManager(context, 1, false));

        // should i show playAll/stopPlayAll buttons
        if(coordinates.size()>0){
            playAll.setVisibility(View.VISIBLE);
            findViewById(R.id.emptyCoordinateListIndicatorPage).setVisibility(View.GONE);
            coordinatesRecyclerView.setVisibility(View.VISIBLE);
        }

        // setup communication with robot
        thread = new Thread(new Runnable() {
            @Override
            public void run() {
                while(running){
                    try {

                        // connectivity checks every 5 seconds (default)
                        if(System.currentTimeMillis() - previous_ping > ping_period){
                            previous_ping = System.currentTimeMillis();
                            sendCommand("");
                        }


                        // send coordinates to arm if user of the app made updates
                        if(updated){
                            updated = false;

                            // save  current position in sharedprefs
                            updatedCurrentPositionInSharedPreferences();

                            sendCommand("motion/?angles=" + bottom + "," + spine + "," + tilt + "," + mouth + "," + gate);
                        }

                        if(playing){
                            updated = true;
                            while(playing){

                                previous_playing_index = playing_index;
                                playing_index -= 1;
                                if(playing_index<0) playing_index = coordinates.size()-1;

                                bottom = coordinates.get(playing_index).bottom;
                                spine = coordinates.get(playing_index).spine;
                                tilt = coordinates.get(playing_index).tilt;
                                mouth = coordinates.get(playing_index).mouth;
                                gate = coordinates.get(playing_index).gate;


                                handler.post(new Runnable() {
                                    public void run() {

                                        // update seekbars
                                        bottomSeekbar.setProgress(bottom);
                                        spineSeekbar.setProgress(spine);
                                        tiltSeekbar.setProgress(tilt);
                                        mouthSeekbar.setProgress(mouth);
                                        gateSeekbar.setProgress(gate);

                                        // update coordinate list
                                        coordinateListAdapter.notifyItemChanged(previous_playing_index);
                                        coordinateListAdapter.notifyItemChanged(playing_index);
                                    }
                                });

                                sendCommand("motion/?angles=" + bottom + "," + spine + "," + tilt + "," + mouth + "," + gate);
                            }
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                        log(e);
                    }
                }
            }
        });
        startThread();

    }

    private void updatedCurrentPositionInSharedPreferences() {
        editor.putString("currentPosition", bottom + "," + spine + "," + tilt + "," + mouth + "," + gate);
        editor.apply();
    }


    private void startThread() {
        running = true;
        thread.start();
    }

    @Override
    protected void onPause() {
        stopThread();
        super.onPause();
    }

    private void updateCoordinatesInSharedPreferences() {

        // save in sharedPreferences
        StringBuilder coordinatesString = new StringBuilder();
        for(Coordinate coordinate: coordinates){
            coordinatesString.append(coordinate.bottom).append(",").append(coordinate.spine).append(",").append(coordinate.tilt).append(",").append(coordinate.mouth).append(",").append(coordinate.gate).append(";");
        }

        String finalCoordinatesString = coordinatesString.length()>0? coordinatesString.substring(0, coordinatesString.length()-2): coordinatesString.toString(); // remove the last semicolumn

        editor.putString("coordinates", finalCoordinatesString);
        editor.apply();
    }

    private void stopThread() {
        running = false;
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
            log(e);
        }
    }


    void sendCommand(String url) {
        log("sending " + url);
        Request request = new Request.Builder()
                .url("http://" + robotIP + "/" + url)
                .get()
                .build();

        try {
            Response response = client.newCall(request).execute();
            if(response.isSuccessful()){
                log("response " + response.body().string());

                // if sent msg was successful, check if our login indicator is saying disconnected just incase
                setConnected(true);
                return;
            } else {
                //log("response unsuccessful");
            }
        } catch(ConnectException e){
            log("couldn't connect " + e);
        } catch(SocketTimeoutException e){
            log("couldn't connect " + e);
        } catch(IOException e){
            log("error when sending http " + e);
            //e.printStackTrace();
        }

        // if we reached this spot then probably a connectivity issue
        setConnected(false);
    }

    private void setConnected(boolean b) {
        if(b){
            if(!connected){
                handler.post(new Runnable() {
                    public void run() {
                        connected = true;
                        connectionIndicator.setText(R.string.connected);
                        applyColor(connectionIndicator, R.color.green);
                    }
                });
            }
        } else {
            if(connected){
                handler.post(new Runnable() {
                    public void run() {
                        connected = false;
                        connectionIndicator.setText(R.string.disconnected);
                        applyColor(connectionIndicator, R.color.red);
                    }
                });
            }
        }
    }


    private void applyColor(TextView element, int color){
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
            element.setTextColor(getColor(color));
        else
            element.setTextColor(getResources().getColor(color));
    }


    public void log(Object log){
        Log.i("HH", String.valueOf(log));
    }

    @Override
    public void play(int index) {
        Coordinate coordinate = coordinates.get(index);

        bottom = coordinate.bottom;
        spine = coordinate.spine;
        tilt = coordinate.tilt;
        mouth = coordinate.mouth;
        gate = coordinate.gate;

        bottomSeekbar.setProgress(bottom);
        spineSeekbar.setProgress(spine);
        tiltSeekbar.setProgress(tilt);
        mouthSeekbar.setProgress(mouth);
        gateSeekbar.setProgress(gate);

        updated = true;

        updatedCurrentPositionInSharedPreferences();
    }

    private int coordinateBeingEdited = -1;
    @Override
    public void notifyToggledMenu(int index) {

        int temp_currently_expanded_coordinate = currently_expanded_coordinate;
        currently_expanded_coordinate = index;
        if(currently_expanded_coordinate!=-1)
            coordinateListAdapter.notifyItemChanged(currently_expanded_coordinate);
        if(temp_currently_expanded_coordinate!=-1)
            coordinateListAdapter.notifyItemChanged(temp_currently_expanded_coordinate);

        if(currently_expanded_coordinate==-1){
            coordinateBeingEdited = -1;

            controlsAdd.setVisibility(View.VISIBLE);
            controlsEdit.setVisibility(View.GONE);
        }

    }

    @Override
    public int getCurrentlyOpened() {
        return currently_expanded_coordinate;
    }

    @Override
    public int whosBeingEdited() {
        return coordinateBeingEdited;
    }

    @Override
    public int whichOneBeingPlayedRn() {
        return playing_index;
    }

    @Override
    public void setBeingEdited(int index) {

        playAll.setVisibility(View.GONE);

        Coordinate coordinate = coordinates.get(index);

        bottom = coordinate.bottom;
        spine = coordinate.spine;
        tilt = coordinate.tilt;
        mouth = coordinate.mouth;
        gate = coordinate.gate;

        bottomSeekbar.setProgress(bottom);
        spineSeekbar.setProgress(spine);
        tiltSeekbar.setProgress(tilt);
        mouthSeekbar.setProgress(mouth);
        gateSeekbar.setProgress(gate);

        coordinateBeingEdited = index;
        controlsAdd.setVisibility(View.GONE);
        controlsEdit.setVisibility(View.VISIBLE);
    }

    @Override
    public void remove(int positionReal) {

        coordinateBeingEdited = -1;
        controlsAdd.setVisibility(View.VISIBLE);
        controlsEdit.setVisibility(View.GONE);

        currently_expanded_coordinate = -1;
        coordinateBeingEdited = -1;
        coordinates.remove(positionReal);
        coordinateListAdapter.notifyDataSetChanged();

        if(coordinates.size()==0){
            playAll.setVisibility(View.GONE);
            findViewById(R.id.emptyCoordinateListIndicatorPage).setVisibility(View.VISIBLE);
            coordinatesRecyclerView.setVisibility(View.GONE);
        } else {
            playAll.setVisibility(View.VISIBLE);
            controlsEdit.setVisibility(View.GONE);
            controlsAdd.setVisibility(View.VISIBLE);
        }

        updateCoordinatesInSharedPreferences();
    }

    @Override
    public void slide(int index, int direction) {
        Coordinate pressed_coordinate = new Coordinate(){{
            bottom = coordinates.get(index).bottom;
            spine = coordinates.get(index).spine;
            tilt = coordinates.get(index).tilt;
            mouth = coordinates.get(index).mouth;
            gate = coordinates.get(index).gate;
        }};

        coordinates.set(index, coordinates.get(index-direction));
        coordinates.set(index-direction, pressed_coordinate);

        coordinateBeingEdited = -1;
        playAll.setVisibility(View.VISIBLE);
        controlsAdd.setVisibility(View.VISIBLE);
        controlsEdit.setVisibility(View.GONE);

        currently_expanded_coordinate = index-direction;
        coordinateListAdapter.notifyItemMoved(index, index-direction);
        coordinateListAdapter.notifyItemChanged(index);
        coordinateListAdapter.notifyItemChanged(index-direction);

        updateCoordinatesInSharedPreferences();
    }

    @Override
    public boolean areWePlaying() {
        return playing;
    }

    public void addCoordinatesClicked(View view) {

        // if the list was empty before adding, then show it now and hide the empty list indicator
        try{
            if(coordinatesRecyclerView.getVisibility()==View.GONE){
                findViewById(R.id.emptyCoordinateListIndicatorPage).setVisibility(View.GONE);
                coordinatesRecyclerView.setVisibility(View.VISIBLE);
            }

            // add the actual coordinates to the list then notify the update
            Coordinate coordinate = new Coordinate();
            coordinate.bottom = bottom;
            coordinate.spine = spine;
            coordinate.tilt = tilt;
            coordinate.mouth = mouth;
            coordinate.gate = gate;
            coordinates.add(0, coordinate);

            playAll.setVisibility(View.VISIBLE);

            // notify update in list
            coordinateListAdapter.notifyDataSetChanged();

            updateCoordinatesInSharedPreferences();

        } catch(Exception e){
            e.printStackTrace();
            log(e);
        }
    }

    public void editCoordinatesClicked(View view) {

        try{
            playAll.setVisibility(View.VISIBLE);

            Coordinate coordinate = new Coordinate();
            coordinate.bottom = bottom;
            coordinate.spine = spine;
            coordinate.tilt = tilt;
            coordinate.mouth = mouth;
            coordinate.gate = gate;

            controlsAdd.setVisibility(View.VISIBLE);
            controlsEdit.setVisibility(View.GONE);

            if(coordinateBeingEdited!=-1){
                coordinates.set(coordinateBeingEdited, coordinate);
                int temp_coordinateBeingEdited = coordinateBeingEdited;
                coordinateBeingEdited = -1;
                currently_expanded_coordinate = -1;
                if(temp_coordinateBeingEdited!=-1)
                    coordinateListAdapter.notifyItemChanged(temp_coordinateBeingEdited);
            }

            updateCoordinatesInSharedPreferences();
        } catch(Exception e){
            e.printStackTrace();
            log(e);
        }
    }

    private int playing_index = 0;
    public void playAllClicked(View view) {


        // flip the buttons
        playAll.setVisibility(View.GONE);
        stopPlayAll.setVisibility(View.VISIBLE);

        // hide any expanded elements
        int temp_currently_expanded_coordinate = currently_expanded_coordinate;
        currently_expanded_coordinate = -1;
        coordinateBeingEdited = -1;
        if(temp_currently_expanded_coordinate!=-1){
            coordinateListAdapter.notifyItemChanged(temp_currently_expanded_coordinate);
        }

        // let's prepare to begin to play
        playing = true;
        playing_index = 0; // ik we supposed to begin from end of list since it's reversed but the loop will automatically step it backward when beginning and loops it over
    }

    public void stopPlayingClicked(View view) {
        playing = false;

        coordinateListAdapter.notifyDataSetChanged();

        playAll.setVisibility(View.VISIBLE);
        stopPlayAll.setVisibility(View.GONE);
    }

    public class Coordinate {
        int bottom=0;
        int spine=0;
        int tilt=0;
        int mouth=0;
        int gate=0;
    }
}
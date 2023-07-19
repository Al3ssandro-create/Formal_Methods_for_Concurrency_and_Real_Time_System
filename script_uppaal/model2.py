model = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
	<declaration>///Constants
const int MAX_POSITION = 73;
const int NUM_PODS =  {placeholder1};
const int NUM_SWITCH = 1;
const int N_STATION = 6;
const int STATION_VARIANCE = 1;
const int STATION_MEAN = 2;
const int POS_POD[NUM_PODS]={placeholder5};
const int previousStations[N_STATION][N_STATION] = {{{{0,0,0,0,0,1}}, {{1,0,0,0,0,0}},{{0,1,0,0,0,0}}, {{0,0,1,0,0,0}},{{0,1,0,0,0,0}},{{0,0,0,1,1,0}}}};
const int SWITCH_POS[NUM_SWITCH]={{50}};
const int station_switch[N_STATION]={{-1,-1,0,0,-1,-1}};
const int NUM_BRANCH[NUM_SWITCH] ={{1}};
const int PODS_BRANCH[NUM_PODS]={placeholder3};
const int LENGTH_BRANCH[NUM_SWITCH][1]={{{{12}}}};
const int SWITCH[NUM_SWITCH] = {{1}}; //TODO: va bene così?Leggendo le specifiche si, ma dobbiamo decidere assieme se farlo cambiare o meno
const int STATION_POSITION[N_STATION]={{13,28,53,59,63,72}};
const int STATION_BRANCH[N_STATION]={{0,0,1,1,0,0}};
const int POS_SENSOR_1[N_STATION] = {{12,27,52,58,62,71}};
const int POS_SENSOR_2[N_STATION] = {{1,17,-1,55,54,69}};
const int POSITION_END_BRANCH[NUM_SWITCH]={{16}};
const int STATION_PROCESSING_TIME[N_STATION]={placeholder6};
const int speedConveyorBelt={placeholder2};
int countHowManyCompleted=0;
int MAX={placeholder7};
int MINIMUM_TIME={placeholder8};
/*** CLOCK ***/
clock beltClock;

//Here we are defining the pods with the auto-instance of Uppaal
typedef int[0,NUM_PODS-1] pod_t;
typedef int[0,N_STATION-1] stat_t;
typedef int [0,N_STATION-1] queue_t;

/*** GLOBAL VARIABLES***/
int pods_switch[NUM_PODS]={placeholder4};
int pos_Id_Station[NUM_PODS];
int pods_position[NUM_PODS];
int pods_position_sorted[NUM_PODS]; //It has all the pods position sorted in modo crescente, it used in the last query
int pods_branch[NUM_PODS]; 
bool pods_blocked[NUM_PODS];
bool stations_blocked[N_STATION];

bool station_free[N_STATION]={{true,true,true,true,true,true}};
bool valSensors[N_STATION][2];

int counter=0; //it is used to select the id to go in the branch

//Tiene traccia del binomio pods_station quando la pods entra nella stazione
typedef struct{{
  int idStation;
  int idPod;
  bool exit1;
}} Station_Pod;
Station_Pod station_pod[N_STATION];

/*** CHANNELS ***/
broadcast chan initializer;
broadcast chan check;
broadcast chan move;
broadcast chan entryStation[N_STATION];
broadcast chan exitStation[N_STATION];
chan StopStations[N_STATION];

chan priority check,move &lt; default &lt; entryStation[N_STATION-1],exitStation[N_STATION-1];

/*** GLOBAL UTILITY FUNCTIONS ************************************************/


void initialize(){{
    int i;
    for(i=0;i&lt;NUM_PODS;i++){{
        pods_position[i]=POS_POD[i];
        pods_branch[i] = PODS_BRANCH[i];
    }}
    
    for(i=0;i&lt;N_STATION;i++){{
       station_pod[i].idStation = i;
       station_pod[i].idPod=-1;
    }}
    for(i=0;i&lt;N_STATION;i++){{
       station_pod[i].exit1 = false;
    }}

}}
void blockNextIfPresent(int id){{
    int i;
    bool flag;
    flag = true;
    while(flag){{
        flag = false;
        for(i = 0; i &lt; NUM_PODS; i++){{
            if(pods_position[i] == pods_position[id]-1 &amp;&amp; pods_branch[i] == pods_branch[id] &amp;&amp; pods_switch[i]== pods_switch[id]){{
                pods_blocked[i]=true;
                flag = true;
                id = i;
            }}
        }}
    }}
}}

void sortPodsPosition(){{
      int i,j,d=0;
    for(d=0;d&lt;NUM_PODS;d++){{
       pods_position_sorted[d]=pods_position[d];
        }}
    for ( i = 0; i &lt; NUM_PODS - 1; i++) {{
        int minIndex = i;
        for ( j = i + 1; j &lt; NUM_PODS; j++) {{
            if (pods_position_sorted[j] &lt; pods_position_sorted[minIndex]) {{
                minIndex = j;
            }}
        }}
        if (minIndex != i) {{
            // Scambia gli elementi arr[i] e arr[minIndex]
            int temp = pods_position_sorted[i];
            pods_position_sorted[i] = pods_position_sorted[minIndex];
            pods_position_sorted[minIndex] = temp;
        }}
    }}
 }}

//this method is called at the end of the branch when the pods needs to be ricongiunta on the main branch
void updateCurrentPositionAfterBranchGlobal(int id,int pos_end_branch){{
       if(pods_position[id]!=MAX_POSITION-1) pods_position[id]=pos_end_branch;
       else pods_position[id]=0;
    
    sortPodsPosition();
}}
// aggiorna la posizione aggiungendo 1, chiamato dalla pods quando avanza 
void updateCurrentPositionGlobal(int id){{
         if(pods_position[id]!=MAX_POSITION-1) pods_position[id]=pods_position[id] + 1;
         else pods_position[id]=0;

     sortPodsPosition();
}}

int getIdPodInPos(int pos, int branch, int switch){{
    int i;
    for(i=0; i&lt;NUM_PODS; i++){{
        if(pods_position[i] == pos &amp;&amp; pods_branch[i] == branch &amp;&amp; pods_switch[i] == switch) return i;
    }}
    return -1;
}}

void checkBlockedGlobal(){{
    int i,j;
    for(i=0; i&lt;NUM_PODS; i++){{
        pods_blocked[i]=false;
    }}
    for(j=0; j&lt;N_STATION; j++){{
        for(i=0; i&lt;NUM_PODS; i++){{
            if(pods_position[i]+1 == POS_SENSOR_1[j] &amp;&amp; pods_branch[i] == STATION_BRANCH[j]  &amp;&amp; getIdPodInPos(pods_position[i]+1, pods_branch[i], pods_switch[i]) != -1 ){{
                  pods_blocked[i]=true;
                  blockNextIfPresent(i);
            }}
        }}
    }}
}}

void setValSensors(int index, int pos, bool value){{
    valSensors[index][pos-1]=value;
}}

//quando la pods entra nella stazione viene aggiornata la struttura dati utilizzata per tenere traccia delle pods nelle stazioni7
//TODO: ma se la station sta subito dopo lo switch?
void enter_station(int id){{ 
    int i,index;
    for(i=0;i&lt;N_STATION;i++){{
            if(STATION_POSITION[i] == pods_position[id]+1 &amp;&amp; STATION_BRANCH[i]==pods_branch[id] &amp;&amp; pods_switch[id] == station_switch[i]
                || pods_position[id] == MAX_POSITION &amp;&amp; STATION_POSITION[i]==0 &amp;&amp; STATION_BRANCH[i]==pods_branch[id] &amp;&amp; station_switch[i]==pods_switch[id]){{
                station_pod[i].idPod=id;
                index=i;
                }}
    }}
    setValSensors(index,1,false);
    checkBlockedGlobal();
}}
 

//chiamata dalla pods, controlla se la stazione in cui è la pods è libera, se è così ritorna true altrimenti ritorna false
bool checkExitStation(int id){{
    int i;
    for(i=0;i&lt;N_STATION;i++){{
        if(station_pod[i].idPod==id &amp;&amp; station_free[station_pod[i].idStation]==true &amp;&amp; station_pod[i].exit1==true ) {{ 
           return true;
        }}
    }}
    return false;
}}
void resetExit(int id){{
    int i;
    for(i=0;i&lt;N_STATION;i++){{
        if(station_pod[i].idPod==id){{
           station_pod[i].exit1=false;
           station_pod[i].idPod=-1;
        }}
     }}
}}

bool checkWaitingGlobal(int id){{
    int i = 0;
    for (i = 0; i &lt; N_STATION; i++ ){{
        if(pods_position[id]==POS_SENSOR_1[i] &amp;&amp; STATION_BRANCH[i]==pods_branch[id])
            return true;
    }}
    return false;
}}

bool checkIfStationGlobal(int id){{
    bool result=false;
    int i;
    for(i=0; i&lt;N_STATION; i++){{
        if(pods_position[id]==STATION_POSITION[i]) result = true;
    }}
    return result;
}}

bool getValSensors(int index, int pos){{
    return valSensors[index][pos-1];
}}

bool checkGlobalPosOccupied(int pos, int branch){{
	int i;
    for(i=0; i&lt;NUM_PODS; i++){{
        if(pods_position[i]==pos &amp;&amp; pods_branch[i]==branch){{
			return true;
        }}
    }}
    return false;
}}

bool checkPodInPos(int pos,int id_sensor){{
    int i;
    if(pos==-1) return false;
    for(i=0; i&lt;NUM_PODS; i++){{
        if(id_sensor!=-1){{
            if(pods_position[i]==pos &amp;&amp; pods_branch[i]==STATION_BRANCH[id_sensor] &amp;&amp; pods_switch[i]==station_switch[id_sensor]) return true;
        }}else{{
             if(pods_position[i]==pos)return true;
        }}
    }}
    return false;
}}

bool checkPodBlockedInPos(int pos, int branch, int switch){{
    int i;
    for(i=0; i&lt;NUM_PODS; i++){{
        if(pods_position[i]==pos &amp;&amp; pods_branch[i] == branch &amp;&amp; pods_switch[i] == switch &amp;&amp; pods_blocked[i] == true ) return true;
    }}
    return false;
}}

bool checkPosIsSensor1(int pos, int branch){{
    int i;
    for(i=0; i&lt;N_STATION; i++){{
        if(POS_SENSOR_1[i]==pos &amp;&amp; STATION_BRANCH[i]==branch) return true;
    }}
    return false;
}}

bool checkPodBlockedInSensor2(int id) {{
    int i;
    for(i=0; i&lt;NUM_PODS; i++){{
        if(pods_position[i]==POS_SENSOR_2[id] &amp;&amp; pods_branch[i]== STATION_BRANCH[id] &amp;&amp; checkPodBlockedInPos(pods_position[i], pods_branch[i], pods_switch[i])) return true;
    }}
    return false;
}}

int getIdStationQueue(int pos, int branch) {{
    int i;
    for(i=0; i&lt;N_STATION; i++){{
        if(POS_SENSOR_1[i]==pos &amp;&amp; STATION_BRANCH[i]==branch) return i;
    }}
    return -1;
}}

void stopStationsGlobal(int id){{
    int i;
    for(i=0; i&lt;N_STATION; i++){{
        if(previousStations[id][i]==1) stations_blocked[i] = true;
    }}
}}

void resumeStationsGlobal(int id){{
    int i;
    for(i=0; i&lt;N_STATION; i++){{
        if(previousStations[id][i]==1) stations_blocked[i] = false;
    }}
}}

//Questo dovrebbe controllare se non c'è una pods nella branch principale
bool otherBranchNotEndedGlobal(int id){{
    bool result = true; 
    int i;
    for(i = 0; i &lt; NUM_PODS; i++){{
//questo idf viene fatto perchè alcune pod aggiornano la propria posizione prima di altre per cui questo if dovrebbe risolvere le cose

        if(id&lt; i){{
            if(pods_position[i]+1 == SWITCH_POS[0]+ POSITION_END_BRANCH[pods_branch[id]-1] &amp;&amp; pods_branch[id]!=pods_branch[i]){{
               return false;
                }}
        }}else if(id&gt;i){{
             if( pods_position[i] == SWITCH_POS[0]+ POSITION_END_BRANCH[pods_branch[id]-1] &amp;&amp; pods_branch[id]!=pods_branch[i]){{
               return false;
             }}
        }}
    }}
    return true;
}}

bool checkSamePositionGlobal(int pod_id){{
    bool result = false;
    int i;
    for(i=0; i&lt;NUM_PODS; i++){{
        if(pods_position[pod_id] != MAX_POSITION - 1){{
            if(i!=pod_id &amp;&amp; pods_position[pod_id]+1 == pods_position[i] &amp;&amp; pods_branch[pod_id] == pods_branch[i] &amp;&amp; pods_switch[pod_id] == pods_switch[i]) result = true;
        }}else{{
            if(pods_position[i]==0) result = true;
        }}
    }}
    return result;
}}

bool queueIsMaximumInSwitch(){{
    int i=0;
    bool pos52=false;
    bool pos51=false;
    for(i=0; i&lt;NUM_PODS;i++){{
        if(pods_position[i] == 52 &amp;&amp; pods_branch[i]==1) pos52=true;
        if(pods_position[i] == 51 &amp;&amp; pods_branch[i]==1) pos51=true;
        }}
    return pos52 &amp;&amp; pos51;
}}</declaration>
	<template>
		<name>Pod</name>
		<parameter>const pod_t id</parameter>
		<declaration>//true because we suppose you are ready and set to false if check go wrong
bool ready = true;
bool waiting = false;
bool station = false;
int idStation = -1;

clock clockPod;


int curr_branch = PODS_BRANCH[id];
int current_pos=  POS_POD[id];



bool isReady(){{
    return ready;
}}

bool isStation(){{
    return station;
}}

bool isBlocked(){{
    return pods_blocked[id];
}}

int retrieve_station(int id){{
    int c=-1;
    int i=0;
    for(i=0; i &lt; N_STATION; i++){{
        if(station_pod[i].idPod==id){{
            c=i;
        }}
    }}
    return c;
}}

void setReadyFalse(){{
    ready=false;
}}

int retrieve_waiting_station(int pos, int branch) {{
    int c=-1;
    int i=0;
    for (i = 0; i &lt; N_STATION; i++ ){{
        if(pos==POS_SENSOR_1[i] &amp;&amp; branch==STATION_BRANCH[i])
            c = i;
    }}
    return c;
}}

void checkWaiting(){{
    if(checkWaitingGlobal(id)) {{
        waiting=true;
        idStation = retrieve_waiting_station(pods_position[id],pods_branch[id]);
    }}
    else {{
        waiting=false;
    }}
}}

void checkBlocked(){{
    if((checkSamePositionGlobal(id) &amp;&amp; checkPodBlockedInPos(pods_position[id]+1, pods_branch[id], pods_switch[id]))
        || (pods_position[id] == MAX_POSITION-1 &amp;&amp; checkPodInPos(0,-1) &amp;&amp; checkPodBlockedInPos(0,0,-1)) 
        || (pods_position[id] == MAX_POSITION-1 &amp;&amp; checkPosIsSensor1(0,0) &amp;&amp; checkPodInPos(0,-1) &amp;&amp; station_free[getIdStationQueue(0,0)]==false) //TODO: checkPosIsSensor1 deve controllare sul branch 0 ?
        || checkPosIsSensor1(pods_position[id]+1, pods_branch[id]) &amp;&amp; checkGlobalPosOccupied(pods_position[id]+1, pods_branch[id]) &amp;&amp;  station_free[getIdStationQueue(pods_position[id]+1,pods_branch[id])]==false 
        ) {{

            pods_blocked[id] = true;
            blockNextIfPresent(id);

    }} else{{     pods_blocked[id] = false;}}
}}

bool isWaiting(){{
    return waiting;
}}



void checkStation(){{
      if(checkIfStationGlobal(id)){{
        station=true;
        ready=false;
    }}
    else{{
        station=false;
        ready=true;
    }}
}}


//TODO: se la branch finisce quando c'è una stazione non vengono aggiornati le branch

void updateCurrentPosition(){{
    int i; 

    checkBlocked();
    if(!pods_blocked[id]){{
// controlla se si è alla fine del branch e se sull'altro branch non arriva un altro pod allo stesso momento
        if(pods_switch[id] != -1 &amp;&amp; current_pos - SWITCH_POS[pods_switch[id]] == LENGTH_BRANCH[pods_switch[id]][curr_branch-1] &amp;&amp; otherBranchNotEndedGlobal(id)){{ //TODO: calcoli giusti? otherBranchNotEnded lo implementiamo in checkBlocked?
            current_pos = SWITCH_POS[pods_switch[id]]+ POSITION_END_BRANCH[curr_branch-1];
            updateCurrentPositionAfterBranchGlobal(id, SWITCH_POS[pods_switch[id]]+ POSITION_END_BRANCH[curr_branch-1]);
            curr_branch = 0;
            pods_switch[id] = -1;
            checkBlockedGlobal();
            

    }}else if(pods_switch[id] != -1 &amp;&amp; current_pos - SWITCH_POS[pods_switch[id]] == LENGTH_BRANCH[pods_switch[id]][curr_branch-1] &amp;&amp; !otherBranchNotEndedGlobal(id)){{
             
     }}else if(current_pos != MAX_POSITION-1  ){{
            current_pos= current_pos + 1;
            updateCurrentPositionGlobal(id);
            checkBlockedGlobal();
            //checkStation();

    // sei alla max position e ricominci il loop
      
            }}else{{
            current_pos=0;
            clockPod=0;
            if(countHowManyCompleted&lt;NUM_PODS) countHowManyCompleted++;
            updateCurrentPositionGlobal(id);
            checkBlockedGlobal();
            
        }}
//assegno la branch se sono nella posizione dello switch e se sono = al countrer
        for(i = 0; i &lt; NUM_SWITCH ; i++){{
            if(SWITCH_POS[i] == current_pos-1 &amp;&amp; id==counter){{
               if(!queueIsMaximumInSwitch()){{
                curr_branch = SWITCH[i];
                pods_switch[id] = i;
                if(counter&lt;NUM_PODS-1)counter++;
                    else counter=0;
            }}
            }}
        }}    
        pods_branch[id]=curr_branch;
    }}
    checkWaiting();
}}

void freeBlocked(){{
    pods_blocked[id] = false;
}}

void initializePod(){{
    checkWaiting();
    checkStation();
    checkBlocked();
}}

void setStationPosition(){{
    pods_position[id] = STATION_POSITION[idStation];
    current_pos = STATION_POSITION[idStation];
    station_pod[idStation].idPod = id;
}}
</declaration>
		<location id="id0" x="-790" y="-178">
		</location>
		<location id="id1" x="-1011" y="-187">
		</location>
		<location id="id2" x="-569" y="-144">
			<name x="-527" y="-161">Ready_to_move</name>
		</location>
		<location id="id3" x="-892" y="-501">
			<name x="-902" y="-535">In_Station</name>
			<label kind="invariant" x="-918" y="-569">beltClock &lt;=speedConveyorBelt</label>
		</location>
		<init ref="id1"/>
		<transition>
			<source ref="id0"/>
			<target ref="id3"/>
			<label kind="guard" x="-1054" y="-365">isWaiting() &amp;&amp; !isBlocked()</label>
			<label kind="synchronisation" x="-1037" y="-348">entryStation[idStation]?</label>
			<label kind="assignment" x="-1011" y="-331">setStationPosition()</label>
		</transition>
		<transition>
			<source ref="id3"/>
			<target ref="id2"/>
			<label kind="guard" x="-773" y="-408">checkExitStation(id)</label>
			<label kind="synchronisation" x="-748" y="-382">exitStation[idStation]?</label>
			<label kind="assignment" x="-714" y="-357">updateCurrentPosition(), resetExit(id), idStation=-1</label>
		</transition>
		<transition>
			<source ref="id2"/>
			<target ref="id0"/>
			<label kind="synchronisation" x="-680" y="-76">move?</label>
			<label kind="assignment" x="-697" y="-59">updateCurrentPosition()</label>
			<nail x="-604" y="-77"/>
			<nail x="-654" y="-85"/>
			<nail x="-731" y="-102"/>
		</transition>
		<transition>
			<source ref="id0"/>
			<target ref="id2"/>
			<label kind="guard" x="-705" y="-187">!isWaiting()</label>
			<label kind="synchronisation" x="-714" y="-153">check?</label>
		</transition>
		<transition>
			<source ref="id1"/>
			<target ref="id0"/>
			<label kind="synchronisation" x="-935" y="-204">initializer?</label>
			<label kind="assignment" x="-952" y="-178">initializePod()</label>
		</transition>
	</template>
	<template>
		<name x="5" y="5">Belt_Handler</name>
		<declaration>




</declaration>
		<location id="id4" x="-518" y="-144">
			<label kind="invariant" x="-654" y="-110">beltClock&lt;=speedConveyorBelt/2</label>
		</location>
		<location id="id5" x="-722" y="-144">
		</location>
		<location id="id6" x="-357" y="-144">
			<label kind="invariant" x="-367" y="-127">beltClock&gt;=speedConveyorBelt/2
 &amp;&amp; beltClock&lt;=speedConveyorBelt</label>
		</location>
		<init ref="id5"/>
		<transition>
			<source ref="id4"/>
			<target ref="id6"/>
			<label kind="guard" x="-500" y="-178">beltClock==speedConveyorBelt/2</label>
			<label kind="synchronisation" x="-459" y="-144">check!</label>
		</transition>
		<transition>
			<source ref="id6"/>
			<target ref="id4"/>
			<label kind="guard" x="-561" y="-306">beltClock==speedConveyorBelt</label>
			<label kind="synchronisation" x="-561" y="-289">move!</label>
			<label kind="assignment" x="-561" y="-272">beltClock:=0</label>
			<nail x="-442" y="-246"/>
			<nail x="-586" y="-246"/>
		</transition>
		<transition>
			<source ref="id5"/>
			<target ref="id4"/>
			<label kind="synchronisation" x="-704" y="-161">initializer!</label>
			<label kind="assignment" x="-704" y="-144">initialize(), beltClock:=0</label>
		</transition>
	</template>
	<template>
		<name x="5" y="5">Station</name>
		<parameter>const stat_t id</parameter>
		<declaration>double mean,variance;
int processing_time=1;// (real processing time is 4) dobbiamo metterlo qua il processing time perchè mi ha dato un sacco di problemi
bool free = true;
clock stationClock;
int count=1;



bool isFree(){{
    if (station_free[id]==true)
        return true;
     else
        return false;
}}

void exit_station(int id){{
     station_pod[id].exit1=true;
}}

void updateCount(){{
    count=count+1;
}}

void freeBlockedPods(){{
    pods_blocked[station_pod[id].idPod] = false;
}}
bool checkNext(int id){{
    int pod_id = station_pod[id].idPod;
    return checkSamePositionGlobal(pod_id);
}}

void initializeStation(){{
    processing_time= STATION_PROCESSING_TIME[id];

    }}

</declaration>
		<location id="id7" x="-705" y="-34">
		</location>
		<location id="id8" x="-238" y="-85">
			<name x="-272" y="-119">Release</name>
			<label kind="invariant" x="-248" y="-68">stationClock &lt;= processing_time</label>
		</location>
		<location id="id9" x="-221" y="-348">
		</location>
		<location id="id10" x="-450" y="68">
			<label kind="invariant" x="-460" y="85">stationClock &lt;= processing_time</label>
		</location>
		<location id="id11" x="-229" y="-433">
			<urgent/>
		</location>
		<location id="id12" x="-960" y="-51">
			<name x="-970" y="-85">START</name>
		</location>
		<init ref="id12"/>
		<transition>
			<source ref="id12"/>
			<target ref="id7"/>
			<label kind="synchronisation" x="-884" y="-76">initializer?</label>
			<label kind="assignment" x="-867" y="-42">initializeStation()</label>
		</transition>
		<transition>
			<source ref="id10"/>
			<target ref="id8"/>
			<label kind="guard" x="-357" y="0">stationClock&gt;=processing_time</label>
		</transition>
		<transition>
			<source ref="id11"/>
			<target ref="id9"/>
		</transition>
		<transition>
			<source ref="id9"/>
			<target ref="id11"/>
			<label kind="guard" x="-433" y="-433">checkNext(id)</label>
			<label kind="synchronisation" x="-296" y="-386">move?</label>
			<nail x="-314" y="-391"/>
		</transition>
		<transition>
			<source ref="id7"/>
			<target ref="id10"/>
			<label kind="guard" x="-952" y="-8">isFree()</label>
			<label kind="synchronisation" x="-952" y="17">entryStation[id]?</label>
			<label kind="assignment" x="-952" y="42">stationClock:=0 , station_free[id]=false</label>
		</transition>
		<transition>
			<source ref="id9"/>
			<target ref="id7"/>
			<label kind="guard" x="-535" y="-238">!checkNext(id)</label>
			<label kind="synchronisation" x="-527" y="-212">exitStation[id]!</label>
			<label kind="assignment" x="-578" y="-187">freeBlockedPods()</label>
		</transition>
		<transition>
			<source ref="id8"/>
			<target ref="id9"/>
			<label kind="guard" x="-212" y="-263">stations_blocked[id]==false</label>
			<label kind="assignment" x="-212" y="-238">station_free[id]=true,exit_station(id)</label>
		</transition>
	</template>
	<template>
		<name>Queue</name>
		<parameter>const queue_t id</parameter>
		<declaration>bool busy = false;
bool stopped = false;
bool ready = false;
bool initialized = false;

bool checkPod1(){{
    return checkPodInPos(POS_SENSOR_1[id],id);
}}

bool checkPod2(){{
    return checkPodInPos(POS_SENSOR_2[id],id);
}}

bool getBusy() {{
    return busy;
}}

void freeBusy(){{
    busy=false;
}}

void initializeQueue(){{
    if(checkPodInPos(POS_SENSOR_1[id],id)){{
        ready = true;
    }}else {{
        ready = false;
    }}
    initialized = true;
}}
</declaration>
		<location id="id13" x="-476" y="-144">
			<name x="-595" y="-187">NotBusy</name>
			<label kind="invariant" x="-603" y="-170">busy == false</label>
		</location>
		<location id="id14" x="-25" y="-136">
			<name x="34" y="-170">Busy</name>
			<label kind="invariant" x="34" y="-144">busy == true &amp;&amp;  beltClock&lt;=speedConveyorBelt</label>
		</location>
		<location id="id15" x="-255" y="136">
			<name x="-230" y="128">StopStationBefore</name>
		</location>
		<location id="id16" x="-841" y="-153">
			<name x="-851" y="-187">Initialized</name>
		</location>
		<location id="id17" x="-1071" y="-153">
			<name x="-1081" y="-187">Start</name>
		</location>
		<init ref="id17"/>
		<transition>
			<source ref="id17"/>
			<target ref="id16"/>
			<label kind="synchronisation" x="-1053" y="-170">initializer?</label>
			<label kind="assignment" x="-1053" y="-153">initializeQueue()</label>
		</transition>
		<transition>
			<source ref="id15"/>
			<target ref="id13"/>
			<label kind="synchronisation" x="-552" y="-17">exitStation[id]?</label>
			<label kind="assignment" x="-731" y="0">stopped=false,busy=false, resumeStationsGlobal(id)</label>
		</transition>
		<transition>
			<source ref="id16"/>
			<target ref="id14"/>
			<label kind="guard" x="-399" y="-408">initialized &amp;&amp; ready</label>
			<label kind="synchronisation" x="-399" y="-425">check?</label>
			<label kind="assignment" x="-399" y="-391">busy = true, enter_station(getIdPodInPos(POS_SENSOR_1[id],STATION_BRANCH[id], station_switch[id]))</label>
			<nail x="-323" y="-365"/>
		</transition>
		<transition>
			<source ref="id16"/>
			<target ref="id13"/>
			<label kind="guard" x="-722" y="-85">initialized &amp;&amp; !ready</label>
			<label kind="synchronisation" x="-722" y="-102">check?</label>
			<nail x="-646" y="-110"/>
		</transition>
		<transition>
			<source ref="id15"/>
			<target ref="id15"/>
			<label kind="guard" x="-255" y="221">stopped==false &amp;&amp; beltClock&lt;=2</label>
			<label kind="assignment" x="-255" y="238">stopped=true, stopStationsGlobal(id)</label>
			<nail x="-255" y="213"/>
			<nail x="-188" y="213"/>
		</transition>
		<transition>
			<source ref="id14"/>
			<target ref="id15"/>
			<label kind="guard" x="-110" y="-34">checkPod2() &amp;&amp; checkPodBlockedInSensor2(id)</label>
			<nail x="-119" y="-25"/>
		</transition>
		<transition>
			<source ref="id14"/>
			<target ref="id13"/>
			<label kind="synchronisation" x="-314" y="-93">exitStation[id]?</label>
			<label kind="assignment" x="-314" y="-76">busy=false</label>
			<nail x="-263" y="-93"/>
		</transition>
		<transition>
			<source ref="id13"/>
			<target ref="id14"/>
			<label kind="guard" x="-552" y="-255">checkPod1()</label>
			<label kind="synchronisation" x="-552" y="-238">entryStation[id]!</label>
			<label kind="assignment" x="-552" y="-221">busy = true, enter_station(getIdPodInPos(POS_SENSOR_1[id], STATION_BRANCH[id], station_switch[id]))</label>
			<nail x="-297" y="-195"/>
		</transition>
	</template>
	<system>// Place template instantiations here.
Process = Belt_Handler();
// List one or more processes to be composed into a system.
system Pod,Station,Queue, Process;
    </system>
	<queries>
		<query>
			<formula>E&lt;&gt; exists(p:pod_t)(Pod(p).current_pos==72 &amp;&amp; Pod(p).clockPod&lt;=MINIMUM_TIME)</formula>
			<comment></comment>
		</query>
        </queries>
</nta>"""
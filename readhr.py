import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import axes as a
from matplotlib.backends.backend_pdf import PdfPages
file_hrdat="Mg6CrFeO8_1_FeCronly_hr.dat"
file_wout="Mg6CrFeO8_1_FeCronly.wout"
start_row_num=-1
import numpy as np
import qEplot_init as I



##################################
### ----- orb_dictの作成 ----- ###
##################################

#orb_dict={ 軌道の番号:[ atm名, 軌道名 ], .... }
with open(file_wout, 'r') as f_wout:
    lines = f_wout.readlines()
    orb_dict = {}
    flag=0
    for i,line in enumerate(lines):
        if ("WF centre and spread" in line) and flag == 1:
            key = int(line.split()[4])
            orb_dict[key] = line.split()[-2:]
        if "Final State" in line: 
            flag = 1

###################################
### ----- DataFrameの作成 ----- ###
###################################
ef=10.5767
with open(file_hrdat, 'r') as f :
    while start_row_num < 10000 :
        list = f.readline().split()
        if ( len(list) == 7 ) and ( "." in list[6] ) : break
        start_row_num+=1

All_hr_df = pd.read_table(file_hrdat, header=start_row_num, \
            delim_whitespace = True, \
            names = [ "x", "y", "z", "orbNo1", "orbNo2", "Ene", "dif" ], \
            dtype = { "x":np.int8, "y":np.int8, "z":np.int8, "orbNo1":np.int16, "orbNo2":np.int16, "Ene":np.float32, "dif":np.float32 } \
)

All_hr_df=All_hr_df.assign( Atm1=[ orb_dict[No][0] for No in All_hr_df["orbNo1"]], \
                            orb1=[ orb_dict[No][1] for No in All_hr_df["orbNo1"]], \
                            Atm2=[ orb_dict[No][0] for No in All_hr_df["orbNo2"]], \
                            orb2=[ orb_dict[No][1] for No in All_hr_df["orbNo2"]] )

unit_hr_df=All_hr_df.query('x==1 and y==0 and z==0')

#same_hr_df = unit_hr_df.query('orbNo1==orbNo2')
#same_hr_df["Ene"] = same_hr_df["Ene"].apply( lambda x: x - ef )

def display_table():
#    df = df.query('orbNo1!=orbNo2')
#    df = unit_hr_df.query('Atm1=="Fe" or Atm1=="Cr"').query('Atm2!="Fe" and Atm2!="Cr"')
#    df = unit_hr_df.query('Atm1=="Fe"').query('Atm2=="Cr"')
#    df = df.query('orb1 =="dxzu" or orb1 == "dyzu" or orb1 == "dxyu"')
    #df = df.query('orb2 =="dz2u" or orb2 == "dx2y2u"')

#    df = df.query('orb1!=orb2')
#    df = df[df["orb1"].str.startswith('d')]
#    df = df[df["orb2"].str.startswith('d')]
#    df = All_hr_df
#    df = df.query('orbNo1==orbNo2')
#    df = df.query('orb1!=orb2')
#    df["Ene"] = df["Ene"].abs()
#    df = df.sort_values('Ene')
#
#    pd.set_option('display.max_rows', None)
    df = unit_hr_df
    df = df.query('Atm1=="Fe"').query('Atm2=="Cr"')
    df = df.query('orb2 =="dz2u" or orb2 == "dx2y2u"')
    with open("hr22","w") as fout:
        print(df,file=fout)
#    df.to_csv("nearef.csv", sep=",")
display_table()

#################################

def cminch(cm: float) -> float:
        return cm * 0.3937

fontdict_title = {
    'family' : 'Times New Roman', 
    'color' : '#000000',
    'size' : 20
}

def Make_Axes_Table(ax_column_width, ax_row_height, height, width ,margin, header, Title):
    ax_column = len(ax_column_width)
    ax_row = len(ax_row_height)
    #----- figのサイズを決め,figを作成 -----#
    fig_width = sum(ax_column_width)+margin*(ax_column+1)
    fig_height = sum(ax_row_height)+margin*(ax_row)+header
    #figwidthとfigheightが縦横比に合うよう、marginを追加する
    rlmargin = tbmargin = 0
    hrate = height
    wrate = width
    if fig_width*hrate > fig_height*wrate :
        tbmargin = (fig_width*hrate/wrate-fig_height)/2
        fig_height = fig_width*hrate/wrate
    elif fig_width*hrate < fig_height*wrate :
        rlmargin = (fig_height*wrate/hrate-fig_width)/2
        fig_width = fig_height*wrate/hrate
    fig = plt.figure(figsize=(cminch(width),cminch(height)))

    #----- Titleの作成 -----#
    header_ycenter=(fig_height-header/2)/fig_height
    fig.text(0.5, header_ycenter, Title, ha='center', va='center', fontdict=fontdict_title, linespacing=1.5)

    #----- Axesの追加 -----#
    ax = [[0] * ax_column  for i in [0] * ax_row]
    for i in range(ax_row):
        k = ax_row - i - 1
        for j in range(ax_column):
            x0 = (sum([ w for w in ax_column_width[:j] ])+margin*(j+1)+rlmargin)/fig_width
            y0 = (sum([ h for h in ax_row_height[:i] ])+margin*(i+1)+tbmargin)/fig_height
            w = ax_column_width[j]/fig_width
            h = ax_row_height[i]/fig_height
            ax[k][j] = fig.add_axes([ x0, y0, w, h ])
    return fig, ax

def Plot_Init(ax: a.Axes):
    ax.xaxis.set_ticks_position('both') #2軸に目盛をつける
    ax.yaxis.set_ticks_position('both')

    #-----枠線太さ(direction=top,bottom,left,right)-----#
    for direction in ax.spines.keys():
        ax.spines[direction].set_linewidth(I.Frame_line_width)

def Eaxis(ax: a.Axes, axis, EneScale):
    Emax = EneScale[0] * EneScale[1] 
    Emin = EneScale[0] * EneScale[2] * -1
    Eticks = np.arange(Emin, Emax+EneScale[0], EneScale[0])
    ax.tick_params( axis, direction="in", pad=I.E_ticks_pad, width=I.ticks_width, length=I.ticks_length )

    #---FermiEne_Line---#
    ax.grid(visible=True, which='major', axis=axis, lw=I.Fermi_line_width, c="black")
    if   axis == 'x': gridlines=ax.get_xgridlines()
    elif axis == 'y': gridlines=ax.get_ygridlines()
    for i, grid in enumerate(gridlines): 
        if i != EneScale[2] : grid.set_linewidth(0)
    return Emax, Emin, Eticks

########################
#----- EneLvPlot ----- #
########################

def EneLvPlot(same_hr_df):
    ax_column_width = [2]
    ax_row_height = [3]
    margin=0.5
    header=0.5
    Title="EneLvPlot"
    fig, ax = Make_Axes_Table(ax_column_width, ax_row_height, 29.7, 21.0, margin, header, Title)

    same_hr_df = same_hr_df.sort_values(by=['Atm1','Ene'],ascending=[True , True])
    #same_hr_df = same_hr_df.query('Atm1=="Fe" or Atm1=="Cr"')
    xlist=same_hr_df['Atm1'].to_list()
    ylist=same_hr_df['Ene'].to_list()
    label=same_hr_df['orb1'].to_list()
    ax[0][0].plot(xlist, ylist, linewidth=0, marker="_", markersize=25 , markeredgewidth=0.01)

    labelheight = 0.15
    for i in range(len(xlist)):
        y=ylist[i]
        if i > 0 and xlist[i]==xlist[i-1] and \
        ylist[i]-y_before < labelheight :
            y = y_before+labelheight
        y_before = y
        strr ="{},{},{},{}".format(xlist[i],label[i],ylist[i],y_before)
        ax[0][0].annotate(label[i] , xy=(xlist[i],y))
        print(strr)

    EneScale=(1,4,4)
    Plot_Init(ax[0][0])
    Emax,Emin,Eticks = Eaxis(ax[0][0], 'y', EneScale)
    ax[0][0].set_yticks(Eticks, minor=False)
    ax[0][0].set_yticklabels(Eticks, fontdict=I.fontdict_Eticks)
    ax[0][0].set_xlim(-1,2)


    SAVE_PATH="."
    OutPutName="EneLvPlot_only"
    plt.savefig("{}/{}".format(SAVE_PATH, OutPutName), format='pdf')


#EneLvPlot(same_hr_df)

########################


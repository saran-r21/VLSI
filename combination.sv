`include "combinational_FSM.sv"
`include "mux_combinational.sv"
`include "Matrix_FM_WM_ADJ_Memory.sv"
`include "Row_Adder.sv"
`include "CounterEdge.sv"


module Combination
#(parameter FEATURE_COLS = 96,
    parameter WEIGHT_ROWS = 96,
    parameter FEATURE_ROWS = 6,
    parameter WEIGHT_COLS = 3,
    parameter FEATURE_WIDTH = 5,
    parameter WEIGHT_WIDTH = 5,
    parameter DOT_PROD_WIDTH = 16,
    parameter ADDRESS_WIDTH = 13,
    parameter COUNTER_WEIGHT_WIDTH = $clog2(WEIGHT_COLS),
    parameter COUNTER_FEATURE_WIDTH = $clog2(FEATURE_ROWS),
    parameter MAX_ADDRESS_WIDTH = 2,
    parameter NUM_OF_NODES = 6,			 
    parameter COO_NUM_OF_COLS = 6,			
    parameter COO_NUM_OF_ROWS = 2,			
    parameter COO_BW = $clog2(COO_NUM_OF_COLS))
(
    input logic clk,
    input logic reset,
    input logic [COO_BW-1:0] coo_in [0:1],
    input logic start,
    input logic [DOT_PROD_WIDTH-1:0] fm_wm_row_data [0:WEIGHT_COLS-1],   
    input logic [COO_BW-1:0] read_row_arg, 

    output logic [COO_BW-1:0] edge_count,
    output logic done,
    output logic [DOT_PROD_WIDTH-1:0] adj_fm_wm_row [0:WEIGHT_COLS-1], 
    output logic [COO_BW-1:0] read_row_fw 
);
    logic Write_Enable_fm_wm_adj;
    logic Counter_Enable_Edge;
    logic FM_WM_Read;
    logic ADJ_FM_WM_Read;
    logic [COO_BW-1 :0] FWA_Read_Row;
    logic [COO_BW-1:0] FWA_Read_Row_muxi;
    logic [DOT_PROD_WIDTH - 1:0] Row_Adder_fm_wm [0: WEIGHT_COLS-1];
    logic [COO_BW -1 :0] COO_IN_NEW [0:1];

    assign COO_IN_NEW[0]= coo_in[0]-1'b1;

    assign COO_IN_NEW[1]= coo_in[1]-1'b1;

    Combinational_MUX CM0(    
    .Selection(FM_WM_Read),
    .Instance0(COO_IN_NEW[0]),
    .Instance1(COO_IN_NEW[1]),
    .Outputt(read_row_fw));   

    Combinational_MUX CM1(    
    .Selection(ADJ_FM_WM_Read),
    .Instance0(COO_IN_NEW[0]),
    .Instance1(COO_IN_NEW[1]),
    .Outputt(FWA_Read_Row_muxi));

    Combinational_MUX CM2(
    .Selection(done),
    .Instance0(FWA_Read_Row_muxi),
    .Instance1(read_row_arg),
    .Outputt(FWA_Read_Row));  

    Matrix_FM_WM_ADJ_Memory MFWADJ0 (.clk(clk),
                                   .rst(reset),
                                   .write_row(FWA_Read_Row_muxi),
                                   .read_row(FWA_Read_Row),
                                   .wr_en(Write_Enable_fm_wm_adj),
                                   .fm_wm_adj_row_in(Row_Adder_fm_wm),  
                                   .fm_wm_adj_out(adj_fm_wm_row)); 
    
    RowAdder RA0(.Value1(fm_wm_row_data),
                  .Value2(adj_fm_wm_row),
                  .FM_WM_Output(Row_Adder_fm_wm));

    CounterEdge CE0(.reset(reset),
                     .Edge_Enable(Counter_Enable_Edge),
                     .clk(clk),
                     .CountIn(edge_count),
                     .count(edge_count));

    Combinational_FSM CF0(.clk(clk),
                          .reset(reset),
                          .edge_count(edge_count),
                          .start(start),
                          .Write_Enable_fm_wm_adj(Write_Enable_fm_wm_adj),
                          .Counter_Enable_Edge(Counter_Enable_Edge),
                          .FM_WM_Read(FM_WM_Read),
                          .ADJ_FM_WM_Read(ADJ_FM_WM_Read), 
                          .done(done));

endmodule


`include "Transformation_FSM.sv"
`include "mux_transformation.sv"
`include "Scratch_Pad.sv"
`include "Vector_Multiplier.sv"
`include "Matrix_FM_WM_Memory.sv"
`include "CounterFeature.sv"
`include "CounterWeight.sv"



module Transformation 
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
  input logic [WEIGHT_WIDTH-1:0] data_in [0:WEIGHT_ROWS-1],
  input logic start,
  input logic [COUNTER_FEATURE_WIDTH-1:0] read_row,


  output logic [ADDRESS_WIDTH-1:0] read_address,
  output logic enable_read,
  output logic [DOT_PROD_WIDTH-1:0] fm_wm_row [0:WEIGHT_COLS-1],
  output logic done
);
    logic [COUNTER_WEIGHT_WIDTH-1 : 0] Count_of_Weight;
    logic [COUNTER_FEATURE_WIDTH-1 : 0] Count_of_Feature; 
    logic [WEIGHT_WIDTH-1 : 0] weight_scratch_pad [0:WEIGHT_ROWS-1];
    logic [DOT_PROD_WIDTH-1 :0] fm_wm_value;
    logic [COUNTER_FEATURE_WIDTH-1:0] read_row_fw;
    logic [COUNTER_FEATURE_WIDTH-1:0] read_row_afw;
    logic enable_write_fm_wm_prod;
    logic enable_write;
    logic enable_scratch_pad;
    logic Weight_Counter_Enable;
    logic enable_feature_counter;
    logic Read_Feature_OR_Weight;
    logic [ADDRESS_WIDTH-1:0] Feature_Address;
    logic [ADDRESS_WIDTH-1:0] Weight_Address;

    Transformation_FSM TF0 ( .clk(clk),
                        .reset(reset),
                        .weight_count(Count_of_Weight),
                        .feature_count(Count_of_Feature),
                        .start(start),
                        .enable_write_fm_wm_prod(enable_write_fm_wm_prod),
                        .enable_read(enable_read),
                        .enable_write(enable_write),
                        .enable_scratch_pad(enable_scratch_pad),
                        .enable_weight_counter(Weight_Counter_Enable),
                        .enable_feature_counter(enable_feature_counter),
                        .read_feature_or_weight(Read_Feature_OR_Weight),
                        .done(done));
    

    Scratch_Pad SP0( .clk(clk),
                     .reset(reset),
                     .write_enable(enable_scratch_pad),
                     .weight_col_in(data_in),
                     .weight_col_out(weight_scratch_pad));
    
    CounterWeight CW0( .reset(reset),
                        .Weight_Enable(Weight_Counter_Enable),
                        .clk(clk),
                        .CountIn(Count_of_Weight),
                        .count(Count_of_Weight));

    VectMultiplier VM0 (.FEATURE_COL(data_in) ,
                           .WEIGHT_ROW(weight_scratch_pad),
                           .PRODUCT(fm_wm_value));
    
    Matrix_FM_WM_Memory MFWM0 (.clk(clk),
                               .rst(reset),
                               .write_row(Count_of_Feature),
                               .write_col(Count_of_Weight), 
                               .read_row(read_row),
                               .wr_en(enable_write_fm_wm_prod),
                               .fm_wm_in(fm_wm_value),
                               .fm_wm_row_out(fm_wm_row));

    CounterFeature CF0(.reset(reset),
                        .Feature_Enable(enable_feature_counter),
                        .clk(clk),
                        .CountIn(Count_of_Feature),
                        .count(Count_of_Feature));

    
    assign Feature_Address = 13'b0001000000000 + Count_of_Feature;
    assign Weight_Address = 13'b0000000000000 + Count_of_Weight;
    Transformation_MUX MT0( .Selection(Read_Feature_OR_Weight),
                            .Instance0(Weight_Address),
                            .Instance1(Feature_Address),
                            .Outputt(read_address));
    

endmodule



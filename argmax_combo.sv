`include "argmax.sv"
`include "argmax_fsm.sv"
`include "Matrix_argmax_Memory.sv"



module argmax
 #(parameter FEATURE_COLS = 96,
    parameter WEIGHT_ROWS = 96,
    parameter FEATURE_ROWS = 6,
    parameter WEIGHT_COLS = 3,
    parameter FEATURE_WIDTH = 5,
    parameter WEIGHT_WIDTH = 5,
    parameter DOT_PROD_WIDTH = 16,
    parameter ADDRESS_WIDTH = 13,
    parameter COUNTER_WEIGHT_WIDTH = $clog2(WEIGHT_COLS),  ///COUNTER_WEIGHT_WIDTH = 2
    parameter COUNTER_FEATURE_WIDTH = $clog2(FEATURE_ROWS),
    parameter MAX_ADDRESS_WIDTH = 2,
    parameter NUM_OF_NODES = 6,			 
    parameter COO_NUM_OF_COLS = 6,			
    parameter COO_NUM_OF_ROWS = 2,			
    parameter COO_BW = $clog2(COO_NUM_OF_COLS)	
)
(
    input logic clk,
    input logic reset,
    input logic start,
    input logic [DOT_PROD_WIDTH-1:0] adj_fm_wm_row [0:WEIGHT_COLS-1],

    output logic done,
    output logic [COO_BW-1 : 0] read_row_arg,
    output logic [MAX_ADDRESS_WIDTH - 1:0] max_addi_answer[0:FEATURE_ROWS-1]
);
    logic [2:0] row_mem;    //sending it to memory for writing
    logic enable_write_argmax;
    logic [COUNTER_WEIGHT_WIDTH-1 :0] fm_wm_adj_row_in;

    argmaxFSM AF0 (.clk(clk),
                    .reset(reset),
                    .start(start),
                    .row_number(read_row_arg),
                    .enable_write_argmax(enable_write_argmax),
                    .done(done));

    ArgmaxCombi AC0(
                    .FM_WM_ADJ_ROW(adj_fm_wm_row),
                    .count(fm_wm_adj_row_in));

    Matrix_argmax_Memory MAM0(.clk(clk),
                              .rst(reset),
                              .write_row(read_row_arg),
                              .read(done),
                              .wr_en(enable_write_argmax),
                              .fm_wm_adj_row_in(fm_wm_adj_row_in),
                              .fm_wm_adj_out(max_addi_answer));

endmodule


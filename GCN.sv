`include "transformation.sv"
`include "combination.sv"
`include "argmax.sv"

module GCN
#(
  // Parameters defining the dimensions and widths of matrices
  parameter FEATURE_COLS = 96,
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
  parameter COO_BW = $clog2(COO_NUM_OF_COLS)
)
(
  // Clock input
  input logic clk,
  
  // Asynchronous reset
  input logic reset,
  
  // Start signal
  input logic start,
  
  // Input data for transformation
  input logic [WEIGHT_WIDTH-1:0] data_in [0:WEIGHT_ROWS-1],
  
  // COO input values
  input logic [COO_BW - 1:0] coo_in [0:1],

  // Output COO address
  output logic [COO_BW - 1:0] coo_address,

  // Output read address
  output logic [ADDRESS_WIDTH-1:0] read_address,
  
  // Output signal to enable read
  output logic enable_read,
  
  // Output signal indicating completion of GCN operation
  output logic done,
  
  // Output array of max addresses
  output logic [MAX_ADDRESS_WIDTH - 1:0] max_addi_answer [0:FEATURE_ROWS - 1],
  
  // Output signals for adj_fm_wm_row to argmax
  output logic [DOT_PROD_WIDTH-1:0] adj_fm_wm_row_to_argmax_out0,
  output logic [DOT_PROD_WIDTH-1:0] adj_fm_wm_row_to_argmax_out1,
  output logic [DOT_PROD_WIDTH-1:0] adj_fm_wm_row_to_argmax_out2
);

  // Internal signals
  logic [COUNTER_FEATURE_WIDTH-1:0] Row_Read_From_Combination;
  logic Transform_done;
  logic Combination_Done;
  logic [DOT_PROD_WIDTH-1 : 0] fm_wm_row_to_comb [0:WEIGHT_COLS-1];
  logic [DOT_PROD_WIDTH-1:0] fm_wm_row [0:WEIGHT_COLS-1];
  logic [DOT_PROD_WIDTH-1:0] adj_fm_wm_row_to_argmax [0:WEIGHT_COLS-1];
  logic [COUNTER_FEATURE_WIDTH-1:0] read_row_arg;

  // Instantiate Transformation module
  Transformation T0 (.clk(clk),
                    .reset(reset),
                    .data_in(data_in),
                    .start(start),
                    .read_row(Row_Read_From_Combination),
                    .read_address(read_address),
                    .enable_read(enable_read),
                    .fm_wm_row(fm_wm_row_to_comb),
                    .done(Transform_done));

  // Assign outputs for adj_fm_wm_row to argmax
  assign adj_fm_wm_row_to_argmax_out0 = adj_fm_wm_row_to_argmax[0];
  assign adj_fm_wm_row_to_argmax_out1 = adj_fm_wm_row_to_argmax[1];
  assign adj_fm_wm_row_to_argmax_out2 = adj_fm_wm_row_to_argmax[2];

  // Instantiate argmax module
  argmax AC0(.clk(clk),
              .reset(reset),
              .start(Combination_Done),
              .adj_fm_wm_row(adj_fm_wm_row_to_argmax),
              .done(done),
              .read_row_arg(read_row_arg),
              .max_addi_answer(max_addi_answer));

  // Instantiate Combination module
  Combination C0(.clk(clk),
                 .reset(reset),
                 .coo_in(coo_in),
                 .start(Transform_done),
                 .fm_wm_row_data(fm_wm_row_to_comb),
                 .read_row_arg(read_row_arg),
                 .edge_count(coo_address),
                 .done(Combination_Done),
                 .adj_fm_wm_row(adj_fm_wm_row_to_argmax),
                 .read_row_fw(Row_Read_From_Combination));
endmodule


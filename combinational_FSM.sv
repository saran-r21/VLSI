module Combinational_FSM 
  #(parameter COO_EDGES = 6,
    parameter COO_BW = $clog2(COO_EDGES))
(
  input logic clk,
  input logic reset,
  input logic [COO_BW-1:0] edge_count,
  input logic start,

  output logic Write_Enable_fm_wm_adj,
  output logic Counter_Enable_Edge,
  output logic FM_WM_Read,
  output logic ADJ_FM_WM_Read, 
  output logic done
);

  // Define an enumeration type for state transitions
  typedef enum logic [2:0] {
    START,
    EDGE1,
    WRITE_ST1,
    EDGE2,
    WRITE_ST2,
    INCREMENT_EDGE_COUNTER,
    DONE
  } state_t;

  // Declare state variables
  state_t current_state, next_state;

  // State machine logic
  always_ff @(posedge clk or posedge reset)
    if (reset)
      current_state <= START;
    else 
      current_state <= next_state;

  always_comb begin
    case (current_state)
      // START state initialization
      START: begin
        Write_Enable_fm_wm_adj = 1'b0;
        Counter_Enable_Edge = 1'b0;
        FM_WM_Read = 1'b0;
        ADJ_FM_WM_Read = 1'b0;
        done = 1'b0;

        // Transition to EDGE1 state when the start signal is asserted
        if (start) begin
          next_state = EDGE1;
        end
        else begin
          next_state = START;
        end
      end

      // EDGE1 state logic
      EDGE1: begin
        Write_Enable_fm_wm_adj = 1'b0;
        Counter_Enable_Edge = 1'b0;
        FM_WM_Read = 1'b0;
        ADJ_FM_WM_Read = 1'b1;
        done = 1'b0;

        // Transition to WRITE_ST1 state
        next_state = WRITE_ST1;
      end

      // WRITE_ST1 state logic
      WRITE_ST1: begin
        Write_Enable_fm_wm_adj = 1'b1;
        Counter_Enable_Edge = 1'b0;
        FM_WM_Read = 1'b0;
        ADJ_FM_WM_Read = 1'b1;
        done = 1'b0;

        // Transition to EDGE2 state
        next_state = EDGE2;
      end

      // EDGE2 state logic
      EDGE2: begin
        Write_Enable_fm_wm_adj = 1'b0;
        Counter_Enable_Edge = 1'b0;
        FM_WM_Read = 1'b1;
        ADJ_FM_WM_Read = 1'b0;
        done = 1'b0;

        // Transition to WRITE_ST2 state
        next_state = WRITE_ST2;
      end

      // WRITE_ST2 state logic
      WRITE_ST2: begin
        Write_Enable_fm_wm_adj = 1'b1;
        Counter_Enable_Edge = 1'b0;
        FM_WM_Read = 1'b1;
        ADJ_FM_WM_Read = 1'b0;
        done = 1'b0;

        // Transition to INCREMENT_EDGE_COUNTER state
        next_state = INCREMENT_EDGE_COUNTER;
      end

      // INCREMENT_EDGE_COUNTER state logic
      INCREMENT_EDGE_COUNTER: begin
        Write_Enable_fm_wm_adj = 1'b0;
        Counter_Enable_Edge = 1'b1;
        FM_WM_Read = 1'b0;
        ADJ_FM_WM_Read = 1'b0;
        done = 1'b0;

        // Transition to DONE state if edge_count is at its maximum
        if (edge_count == COO_EDGES - 1) begin
          next_state = DONE;  
        end
        // Otherwise, transition back to EDGE1
        else begin
          next_state = EDGE1;
        end
      end

      // DONE state logic
      DONE: begin
        Write_Enable_fm_wm_adj = 1'b0;
        Counter_Enable_Edge = 1'b0;
        FM_WM_Read = 1'b0;
        ADJ_FM_WM_Read = 1'b0;
        done = 1'b1;

        // Stay in DONE state
        next_state = DONE;
      end

    endcase
  end

endmodule


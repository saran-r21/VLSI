module argmaxFSM
#(parameter FEATURE_ROWS = 6,
    parameter WEIGHT_COLS = 3,
    parameter COUNTER_WEIGHT_WIDTH = $clog2(WEIGHT_COLS),
    parameter COUNTER_FEATURE_WIDTH = $clog2(FEATURE_ROWS))
(
    input logic clk,
    input logic reset,
    input logic start,

    output logic [2:0] row_number,
    output logic [2:0] row,
    output logic enable_write_argmax,
    output logic done
);
typedef enum logic [2:0] {
	START,
    ROW1,
    ROW2,
    ROW3,
    ROW4,
    ROW5,
    ROW6,
    ROW7
  } state_t;

  state_t current_state, next_state;

  always_ff @(posedge clk or posedge reset)
    if (reset)
      current_state <= START;
    else
      current_state <= next_state;

  always_comb begin
    case (current_state)
    
    START: begin
        row_number = 3'b000;
        row = 3'b000;
        enable_write_argmax = 1'b0;
        done = 1'b0;

        if (start) begin
            next_state = ROW1;
        end
        else begin
            next_state = START;
        end
    end

    ROW1: begin
        row_number = 3'b001;
        row=3'b000;
        enable_write_argmax = 1'b1;
        done = 1'b0;

        next_state = ROW2;
    end

    ROW2: begin
        row_number = 3'b010;
        row=3'b001;
        enable_write_argmax = 1'b1;
        done = 1'b0;

        next_state = ROW3;
    end

    ROW3: begin
        row_number = 3'b011;
        row=3'b010;
        enable_write_argmax = 1'b1;
        done = 1'b0;

        next_state = ROW4;
    end

    ROW4: begin
        row_number = 3'b100;
        row=3'b011;
        enable_write_argmax = 1'b1;
        done = 1'b0;

        next_state = ROW5;
    end

    ROW5: begin
        row_number = 3'b101;
        row=3'b100;
        enable_write_argmax = 1'b1;
        done = 1'b0;

        next_state = ROW6;
    end

    ROW6: begin
        row_number = 3'b101;
        row=3'b101;
        enable_write_argmax = 1'b1;
        done = 1'b0;

        next_state = ROW7;
    end

    ROW7: begin
        row_number = 3'b101;
        row=3'b101;
        enable_write_argmax = 1'b0;
        done = 1'b1;

        next_state = ROW7;
    end

    endcase

  end

endmodule


import threading
from pymacro.backend.state import StateMachine, GraphNode
from tkinter import messagebox

class GraphManager:
    def __init__(self, ui_canvas):
        """
        ui_canvas: instance of GraphCanvas containing NodeWidget + EdgeWidget lists.
        """
        self.ui_canvas = ui_canvas
        self.state_machine = None
        self._thread = None

    def build_state_machine(self):
        """
        1) For each Observer‐type NodeWidget, build a GraphNode:
             GraphNode(observer=... , actions=[...], next_node=...)
        2) Link their .next_node according to the UI edges.
        3) Return the first GraphNode (or None if there are no observers).
        """
        # Map from NodeWidget → GraphNode:
        node_to_graphnode = {}

        # Step A: Create a GraphNode for every Observer NodeWidget:
        for ui_node in self.ui_canvas.nodes:
            if ui_node.type == "Observer":
                backend_obs = ui_node.backend_observer
                # If the user never called select_bbox, fallback to a no-op observer:
                if not backend_obs:
                    from pymacro.backend.observer import RegionObserver
                    backend_obs = RegionObserver(region=(0,0,1,1), threshold=999999)
                # Gather any ActionConnected directly from this observer:
                # In your UI, outgoing edges from an Observer must go to exactly one Action–node.
                actions = []
                if ui_node.outgoing:
                    # There should only be ONE outgoing UI edge from an observer → action
                    action_node = ui_node.outgoing[0]
                    # Each Action‐node has a list of node.backend_actions:
                    actions = action_node.backend_actions.copy()

                graphnode = GraphNode(observer=backend_obs, actions=actions)
                node_to_graphnode[ui_node] = graphnode

        # Step B: Link each GraphNode.next_node according to the UI graph logic:
        #   - If Observer O → Action A, then find the NEXT observer that A points to.
        #   - If Action A → Action B (i.e. a chain of actions), include B’s backend_actions
        #     as part of the same GraphNode.actions list. Then continue until we hit an Observer.
        #
        # The simplest approach: for each observer‐UI, follow outgoing edge to action_UI,
        # then follow that action_UI’s outgoing edges (if any) until you hit another observer_UI.
        for ui_node, graphnode in node_to_graphnode.items():
            # Start from the observer node: see what Action(s) it points to:
            if ui_node.outgoing:
                action_ui = ui_node.outgoing[0]
                # Now follow a chain of Action→Action until you find an Observer, or run out:
                action_chain = [action_ui]
                while True:
                    # Take the last action in chain
                    last_action_node = action_chain[-1]
                    # If that action has outgoing to another action:
                    out_list = last_action_node.outgoing
                    if out_list and out_list[0].type == "Action":
                        action_chain.append(out_list[0])
                        continue
                    # If that action points to an Observer, break:
                    if out_list and out_list[0].type == "Observer":
                        next_obs_ui = out_list[0]
                        graphnode.next_node = node_to_graphnode.get(next_obs_ui, None)
                    break

                # Finally, flatten the entire chain’s backend_actions into graphnode.actions
                all_backend_actions = []
                for act_ui in action_chain:
                    all_backend_actions.extend(act_ui.backend_actions)
                graphnode.actions = all_backend_actions

        # Step C: Determine a “start” node. For now, pick the first Observer in canvas.nodes:
        #   (you could also add a UI‐toggle to mark one observer as “start”)
        start = None
        for ui_node in self.ui_canvas.nodes:
            if ui_node.type == "Observer":
                start = node_to_graphnode[ui_node]
                break

        return start

    def run(self):
        """
        1) Build the StateMachine from UI graph
        2) Launch it in a separate thread
        """
        start_graphnode = self.build_state_machine()
        if not start_graphnode:
            messagebox.showwarning("Run", "No observer node found—cannot run.")
            return

        self.state_machine = StateMachine(start_node=start_graphnode)

        def target():
            self.state_machine.run()

        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stop the running StateMachine.
        """
        if self.state_machine:
            self.state_machine.stop()
            self._thread.join(timeout=1)
            self.state_machine = None
            self._thread = None

{
  description = "CS:GO Visualizer dev shell with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python311;

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      pythonSet =
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            nixpkgs.lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
            ]
          );

      editableOverlay = workspace.mkEditablePyprojectOverlay { root = "$REPO_ROOT"; };

      devPythonSet = pythonSet.overrideScope (nixpkgs.lib.composeManyExtensions [ editableOverlay ]);

      virtualenv = devPythonSet.mkVirtualEnv "dev-env" workspace.deps.all;
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          virtualenv
          pkgs.uv
        ];

        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        # // nixpkgs.lib.optionalAttrs pkgs.stdenv.isLinux {
        #   LD_LIBRARY_PATH = nixpkgs.lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
        # };

        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          echo "✅ uv2nix dev shell ready!"
        '';
      };
    };
}

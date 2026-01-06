"""Protein structure analysis tools using BioPython."""

from typing import Any

from Bio.PDB import PDBList, PDBParser


def fetch_pdb_structure(pdb_id: str, file_format: str = "pdb") -> dict[str, Any]:
    """
    Fetch a protein structure from the PDB database.

    Args:
        pdb_id: PDB identifier (e.g., '1ABC')
        file_format: File format - 'pdb' or 'cif' (default: 'pdb')

    Returns:
        Dictionary containing structure information and file location
    """
    try:
        pdb_id = pdb_id.upper()
        pdbl = PDBList()

        file_path = pdbl.retrieve_pdb_file(
            pdb_id, pdir=".", file_format=file_format, overwrite=True
        )

        return {
            "success": True,
            "pdb_id": pdb_id,
            "format": file_format,
            "file_path": file_path,
            "message": f"Structure {pdb_id} downloaded successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "pdb_id": pdb_id}


def calculate_structure_stats(pdb_file: str) -> dict[str, Any]:
    """
    Calculate statistics for a PDB structure file.

    Args:
        pdb_file: Path to PDB file

    Returns:
        Dictionary containing structure statistics
    """
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("structure", pdb_file)

        num_models = len(structure)
        num_chains = sum(len(model) for model in structure)
        num_residues = sum(len(chain) for model in structure for chain in model)
        num_atoms = sum(len(residue) for model in structure for chain in model for residue in chain)

        chain_info = []
        for model in structure:
            for chain in model:
                chain_id = chain.get_id()
                chain_length = len(chain)
                chain_info.append({"chain_id": chain_id, "num_residues": chain_length})

        return {
            "success": True,
            "file": pdb_file,
            "num_models": num_models,
            "num_chains": num_chains,
            "num_residues": num_residues,
            "num_atoms": num_atoms,
            "chains": chain_info,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "file": pdb_file}


def find_active_site(
    pdb_file: str, residue_numbers: list[int], chain_id: str = "A"
) -> dict[str, Any]:
    """
    Extract information about specific residues (e.g., active site).

    Args:
        pdb_file: Path to PDB file
        residue_numbers: List of residue numbers to analyze
        chain_id: Chain identifier (default: 'A')

    Returns:
        Dictionary containing active site residue information
    """
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("structure", pdb_file)

        model = structure[0]
        chain = model[chain_id]

        active_site_info = []

        for res_num in residue_numbers:
            try:
                residue = chain[res_num]
                res_name = residue.get_resname()
                atoms = [atom.get_name() for atom in residue]

                active_site_info.append(
                    {
                        "residue_number": res_num,
                        "residue_name": res_name,
                        "num_atoms": len(atoms),
                        "atoms": atoms,
                    }
                )
            except KeyError:
                active_site_info.append(
                    {
                        "residue_number": res_num,
                        "error": f"Residue {res_num} not found in chain {chain_id}",
                    }
                )

        return {
            "success": True,
            "file": pdb_file,
            "chain_id": chain_id,
            "num_residues_analyzed": len(residue_numbers),
            "active_site": active_site_info,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "file": pdb_file, "chain_id": chain_id}

const UploadBtn = document.getElementById("Upload");
const FileInput = document.getElementById("FileInput");
const OutputPreview = document.getElementById("OutputPreview");
const StartBtn = document.getElementById("Start");
const InputPreview = document.getElementById("InputPreview");

let Puzzle;

UploadBtn.addEventListener("click", function()
{
	FileInput.click();
});

FileInput.addEventListener("change", async function()
{
	if (FileInput && FileInput.files[0])
	{
		const File = FileInput.files[0];

		const data = new FormData();
		data.append("InputFile",File)

		try
		{
			const Response = await fetch("/process",{
				method: "POST",
				body: data
			});

			const Data = await Response.json();

			if (Data.Ret)
			{
				Puzzle = Data.Image;
				InputPreview.src = Data.Image;
				StartBtn.disabled = false;
			}
		}
		catch (error)
		{
			console.error("Error: ",error);
		}
	}
});

StartBtn.addEventListener("click", async function()
{
	StartBtn.disabled = true;
	UploadBtn.disabled = true;

	const data = new FormData();
	data.append("InputFile",Puzzle);

	try
	{
		const Response = await fetch("/solve",{
			method: "POST",
			body: data
		});

		const Data = await Response.json();

		if (Data.Ret)
		{
			OutputPreview.src = Data.Image;
			alert("Puzzle Solved!");
			UploadBtn.disabled = false;
		}
	}
	catch (error)
	{
		console.error("Error: ",error);
	}
});

StartBtn.disabled = true;
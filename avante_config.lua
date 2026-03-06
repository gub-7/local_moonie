-- Avante.nvim configuration for moonshot-local
-- Add this to your Neovim config

return {
  "yetone/avante.nvim",
  event = "VeryLazy",
  opts = {
    -- Use moonshot_local as the provider
    provider = "moonshot_local",
    
    behaviour = {
      -- Fast Apply requires separate Morph service
      enable_fastapply = false,
    },
    
    providers = {
      moonshot_local = {
        -- Inherit OpenAI-compatible behavior
        __inherited_from = "openai",
        
        -- Point to local proxy
        endpoint = "http://127.0.0.1:8080/v1",
        
        -- API key from environment
        api_key_name = "MOONSHOT_LOCAL_API_KEY",
        
        -- Model name
        model = "moonshot-local",
        
        -- Optional: adjust temperature
        temperature = 0.2,
        max_tokens = 4096,
      },
    },
  },
  
  -- Add other Avante dependencies as needed
  dependencies = {
    "stevearc/dressing.nvim",
    "nvim-lua/plenary.nvim",
    "MunifTanjim/nui.nvim",
    "nvim-tree/nvim-web-devicons",
  },
}

